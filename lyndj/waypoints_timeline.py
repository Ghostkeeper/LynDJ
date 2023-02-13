# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import PySide6.QtCore  # For custom properties.
import PySide6.QtQuick  # This class extends QQuickPaintedItem.
import PySide6.QtSvg  # To render the graph.
import time  # To generate timestamps for the graph.

import lyndj.metadata  # To get the waypoints of a song.
import lyndj.player  # To get the current play time.
import lyndj.theme  # To get the colours to draw the graph in.

def colour_to_hex(colour) -> str:
	"""
	Converts a QColor colour to a hex string that can be inserted in SVG code.

	Transparency (the alpha channel) is not taken into account.
	:param colour: A colour as obtained from the theme.
	:return: A hex string appropriate for SVG.
	"""
	colour = [colour.red(), colour.green(), colour.blue()]
	result = ""
	for component in colour:
		component = hex(component)[2:]
		if len(component) < 2:
			component = "0" * (2 - len(component)) + component
		result += component
	return result


class WaypointsTimeline(PySide6.QtQuick.QQuickPaintedItem):
	"""
	This is a QML item that draws a waypoint graph on the screen, using lines and circles.

	The waypoints are drawn with the SVG painter implementation, but the SVG being drawn is dynamically generated from
	a given set of waypoints. The colours of the graph are also automatically adjusted to the theme, so no recolouring
	is necessary.
	"""

	line_width = 2
	"""
	The width to draw the lines and the outline of the nodes.
	"""

	node_radius = 3
	"""
	The radius to draw the nodes with.
	"""

	colour = "000000"
	"""
	The colour of the lines and nodes.
	"""

	background_colour = "FFFFFF"
	"""
	The fill colour of the nodes.
	"""

	@classmethod
	def parse_waypoints(cls, waypoints_serialised) -> list:
		"""
		Parses a waypoints string to produce the waypoints it represents.

		The format of the waypoints serialisation is human-readable and quite simple.
		* The waypoints are separated by pipes, and are ordered by timestamp.
		* Each individual waypoint consists of two floating point numbers, separated by semicolons.
		* The first of the numbers represents the timestamp at which this waypoint occurs.
		* The second of the numbers represents the level that must be achieved in this timestamp.

		For example, a waypoint string may look like this:
		``64.224167;0.5|66.224167;0.8|77.245023;0.8|77.2245023;0.4``
		:param waypoints_serialised: A string representing a list of waypoints.
		:return: The list of waypoints it represents, as list of tuples. The first element of each tuple is the
		timestamp in seconds. The second is the level between 0 and 1.
		"""
		if waypoints_serialised == "":
			return []

		result = []
		waypoints_list = waypoints_serialised.split("|")
		for waypoint_str in waypoints_list:
			waypoint_parts = waypoint_str.split(";")
			if len(waypoint_parts) != 2:  # Incorrectly formatted. Each waypoint should be 2 numbers separated by a semicolon.
				logging.warning(f"Incorrectly formatted waypoint: {waypoint_str}")
				continue  # Skip.
			try:
				timestamp = float(waypoint_parts[0])
				level = float(waypoint_parts[1])
			except ValueError:
				logging.warning(f"Incorrectly formatted float in waypoint: {waypoint_str}")
				continue  # Skip.
			result.append((timestamp, level))
		return result

	@classmethod
	def serialise_waypoints(cls, waypoints):
		"""
		Serialise the waypoints to a string, so that it can be stored in a database.

		For a reference to the format of this serialisation, see the parse_waypoints function documentation.
		:param waypoints: A list of waypoints to serialise.
		:return: A string representing that list of waypoints.
		"""
		return "|".join([";".join([str(part) for part in waypoint]) for waypoint in waypoints])

	def __init__(self, parent=None) -> None:
		"""
		Creates a timeline element that shows and interacts with the waypoints for a certain property of songs.
		:param parent: The parent QML element to store this element under.
		"""
		super().__init__(parent)
		self.current_path = ""  # The path to the song, used to reference the metadata and store any changes to the waypoints.
		self.current_field = ""  # The type of waypoints to show and adjust, e.g. volume, bass, mids or treble. This should be one of the metadata fields of the song.
		self.svg = ""
		self.renderer = None  # To be filled by the initial call to update_visualisation.
		self.duration = 0  # We need to know the duration of the song in order to draw the timestamps in the correct place.

		# When we are playing a song, we have a more accurate duration (stripped from silence).
		lyndj.player.Player.get_instance().is_playing_changed.connect(self.update_duration)

		# If a transition is currently being made, store the start time of that transition until we can add the complete transition.
		self.ongoing_transition_start_time = None

		self.colour = colour_to_hex(lyndj.theme.Theme.get_instance().colours["foreground"])
		self.background_colour = colour_to_hex(lyndj.theme.Theme.get_instance().colours["background"])

		# When resizing the image, we must re-render.
		self.widthChanged.connect(self.generate_graph)
		self.heightChanged.connect(self.generate_graph)

		# Fill the waypoint data from the metadata of the file, then generate the initial graph.
		self.waypoints = []
		self.generate_graph()

	path_changed = PySide6.QtCore.Signal()
	"""
	Triggered when the path changes of the file to display the waypoints for.
	"""

	def set_path(self, new_path) -> None:
		"""
		Change the current path.
		:param new_path: The new path to store the waypoints of.
		"""
		self.current_path = new_path
		try:
			self.waypoints = self.parse_waypoints(lyndj.metadata.get(new_path, self.current_field))  # Update the waypoints to represent the new path.
		except KeyError:  # Path doesn't exist. Happens at init when path is still empty string.
			self.waypoints = []
		self.update_duration()
		self.generate_graph()

	@PySide6.QtCore.Property(str, fset=set_path, notify=path_changed)
	def path(self) -> str:
		"""
		Get the currently assigned song path.
		:return: The path to the track that this item represents the waypoints of.
		"""
		return self.current_path

	field_changed = PySide6.QtCore.Signal()
	"""
	Triggered when the field changes to display for the file.
	"""

	def set_field(self, new_field) -> None:
		"""
		Change the current metadata field to display.
		:param new_field: The new field to display.
		"""
		self.current_field = new_field
		if self.current_path == "":
			self.waypoints = []
		else:
			self.waypoints = self.parse_waypoints(lyndj.metadata.get(self.current_path, new_field))  # Update the waypoints to represent the new path.
		self.generate_graph()

	@PySide6.QtCore.Property(str, fset=set_field, notify=field_changed)
	def field(self) -> str:
		"""
		Get the currently assigned metadata field that is displayed.

		For example, you can display the volume, bass, mids or treble. This should be one of the metadata fields of the
		file.
		:return: The metadata field containing waypoints that is displayed in this image.
		"""
		return self.current_field

	def update_duration(self):
		"""
		Set the duration field to the latest known information.

		If a song is playing, it'll use the duration of that song.
		If no song is playing, it'll get the duration from the metadata of the current path.
		"""
		if lyndj.player.Player.current_track is not None:
			self.duration = len(lyndj.player.Player.current_track) / 1000.0
		elif self.current_path == "":
			self.duration = 0
		else:
			self.duration = lyndj.metadata.get(self.current_path, "duration")

	def generate_graph(self) -> None:
		"""
		Re-generates the SVG data to draw.
		"""
		width = self.width()
		height = self.height()
		svg = f"<svg version=\"1.0\" width=\"{width}\" height=\"{height}\">\n"

		if len(self.waypoints) > 0:
			nodes = []
			polyline = ""
			for timestamp, level in self.waypoints:
				if len(nodes) == 0:  # First node attaches to the left side with a horizontal line.
					polyline += f"M0,{(1 - level) * height}"
				x = width * timestamp / self.duration
				y = (1 - level) * height
				nodes.append(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"{self.node_radius}\" />")
				polyline += f" L{x},{y}"
			if polyline == "":  # Without any nodes, the volume is always at the default.
				polyline += f"M0, {height / 2}"
			polyline += f" H{width}"
			svg += f"<g stroke=\"#{self.colour}\" stroke-width=\"{self.line_width}\" fill=\"#{self.background_colour}\">\n"
			svg += f"<path fill=\"none\" d=\"{polyline}\" />\n"
			svg += "\n".join(nodes)
			svg += "</g>\n"
		svg += "</svg>"

		self.svg = svg
		self.renderer = PySide6.QtSvg.QSvgRenderer(svg.encode("UTF-8"))
		self.update()

	def paint(self, painter) -> None:
		"""
		Renders the visualisation to the screen.
		:param painter: A painter object that can paint to the screen.
		"""
		if self.renderer:
			self.renderer.render(painter)  # Simply forward to the renderer.

	def add_transition(self, time_start, time_end, level_end) -> None:
		"""
		Inserts a transition to the waypoints of this song.

		The starting point of the transition will determine the level of the start point. If this transition overlaps
		with another transition's starting point, that transition will be erased in favour of the new one.
		:param time_start: The timestamp of the start of the transition, in seconds.
		:param time_end: The timestamp of the end of the transition, in seconds.
		:param level_end: The level at the end of the transition, between 0 and 1.
		"""
		# First find where in the current set of transitions this new transition starts.
		for pos_start in range(len(self.waypoints)):
			if self.waypoints[pos_start][0] > time_start:
				break  # Insert before this waypoint.
		else:
			pos_start = len(self.waypoints)

		# Test whether this waypoint is within a transition or in between transitions.
		if pos_start == 0:
			starts_within = False  # Before the first waypoint is never inside of a transition.
		elif pos_start == len(self.waypoints):
			starts_within = False  # After the last waypoint is never inside of a transition.
		elif self.waypoints[pos_start - 1][1] == self.waypoints[pos_start][1]:
			starts_within = False  # If the levels around the new waypoint are the same, that's not within a transition.
		else:
			starts_within = True

		# Test how many waypoints are overridden by the transition.
		pos_end = pos_start
		for pos_end in range(pos_start, len(self.waypoints)):
			if self.waypoints[pos_end][0] > time_end:
				break
		# If the end waypoint is within a transition, expand the end position by 1 to also remove the end of that transition.
		if pos_end != 0 and pos_end != len(self.waypoints) and self.waypoints[pos_end - 1][1] != self.waypoints[pos_end][1]:
			pos_end += 1


		# Figure out the starting level.
		if pos_start == 0:  # Must be the starting level then, i.e. the starting level of the first transition.
			if len(self.waypoints) == 0:  # No transitions.
				level_start = 0.5  # Default level.
			else:
				level_start = self.waypoints[0][1]
		elif starts_within:  # Halfway between waypoints, so interpolate the level.
			time_before = self.waypoints[pos_start - 1][0]
			ratio = (time_start - time_before) / (self.waypoints[pos_start][0] - time_before)
			level_before = self.waypoints[pos_start - 1][1]
			level_start = level_before + ratio * (self.waypoints[pos_start][1] - level_before)
		else:  # Between transitions, so it's easy then. Just take the level from either side, since they are the same.
			level_start = self.waypoints[pos_start - 1][1]  # (Actually, do take before since it might also be after the last one.)

		# If there are waypoints afterwards, adjust the next waypoint to honour the new current volume.
		if pos_end < len(self.waypoints) - 1 and self.waypoints[pos_end - 1][1] == self.waypoints[pos_end][1]:
			self.waypoints[pos_end] = (self.waypoints[pos_end][0], level_end)

		# Remove the waypoints that would get overridden.
		del self.waypoints[pos_start : pos_end]
		# Insert the new waypoints.
		self.waypoints.insert(pos_start, (time_start, level_start))
		self.waypoints.insert(pos_start + 1, (time_end, level_end))

		# Store this information and re-render.
		lyndj.metadata.change(self.current_path, self.current_field, self.serialise_waypoints(self.waypoints))
		self.generate_graph()
		self.update()

	@PySide6.QtCore.Slot()
	def start_transition(self) -> None:
		"""
		Triggered when a transition is started by the user.

		This stores the start time and start value of the transition.
		:param start_time: The time when the transition started.
		"""
		if lyndj.player.Player.start_time is None:
			return  # No song is currently playing.
		current_time = time.time() - lyndj.player.Player.start_time
		logging.debug(f"Starting transition at {current_time}")
		self.ongoing_transition_start_time = current_time

	@PySide6.QtCore.Slot(float)
	def end_transition(self, end_level):
		"""
		Triggered when a transition is ended by the user.

		This takes the ongoing transition start time and the end time and end level, to insert a full new transition.
		:param end_time: The time when the transition ends.
		:param end_level: The level at which the transition ends.
		"""
		if lyndj.player.Player.start_time is None:
			return  # No song is currently playing.
		if self.ongoing_transition_start_time is None:
			logging.error("Trying to end a transition before starting it.")
			return
		current_time = time.time() - lyndj.player.Player.start_time
		logging.debug(f"Ending transition from {self.ongoing_transition_start_time} to {current_time}, level {end_level}.")
		self.add_transition(self.ongoing_transition_start_time, current_time, end_level)
		self.ongoing_transition_start_time = None  # Reset this one for the next transition.