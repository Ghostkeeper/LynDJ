# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import PySide6.QtCore  # For custom properties.
import PySide6.QtQuick  # This class extends QQuickPaintedItem.
import PySide6.QtSvg  # To render the graph.

import metadata  # To get the waypoints of a song.
import theme  # To get the cololurs to draw the graph in.

class WaypointsTimeline(PySide6.QtQuick.QQuickPaintedItem):
	"""
	This is a QML item that draws a waypoint graph on the screen, using lines and circles.

	The waypoints are drawn with the SVG painter implementation, but the SVG being drawn is dynamically generated from
	a given set of waypoints. The colours of the graph are also automatically adjusted to the theme, so no recolouring
	is necessary.
	"""

	@classmethod
	def colourToHex(cls, colour) -> str:
		"""
		Converts a QColor colour to a hex string that can be inserted in SVG code.

		Transparency (the alpha channel) is not taken into account.
		:param colour: A colour as obtained from the theme.
		:return: A hex string appropriate for SVG.
		"""
		return hex(colour.red()) + hex(colour.green()) + hex(colour.blue())

	line_width = 2
	"""
	The width to draw the lines and the outline of the nodes.
	"""

	node_radius = 3
	"""
	The radius to draw the nodes with.
	"""

	colour = colourToHex(theme.Theme.getInstance().colours["foreground"])
	"""
	The colour of the lines and nodes.
	"""

	background_colour = colourToHex(theme.Theme.getInstance().colours["background"])
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

	def __init__(self, field, parent=None) -> None:
		"""
		Creates a timeline element that shows and interacts with the waypoints for a certain property of songs.
		:param path:
		:param field: The type of waypoints to show and adjust, e.g. volume, bass, mids or treble. This should be one of
		the metadata fields of the song.
		:param parent: The parent QML element to store this element under.
		"""
		super().__init__(parent)
		self.current_path = ""  # The path to the song, used to reference the metadata and store any changes to the waypoints.
		self.current_field = field
		self.svg = ""
		self.renderer = None  # To be filled by the initial call to update_visualisation.
		self.duration = 0  # We need to know the duration of the song in order to draw the timestamps in the correct place.

		# Fill the waypoint data from the metadata of the file, then generate the initial graph.
		self.waypoints = []
		self.generate_graph()

	path_changed = PySide6.QtCore.Signal()

	def set_path(self, new_path) -> None:
		"""
		Change the current path.
		:param new_path: The new path to store the waypoints of.
		"""
		self.current_path = new_path
		try:
			self.waypoints = self.parse_waypoints(metadata.get(new_path, self.current_field))  # Update the waypoints to represent the new path.
		except KeyError:  # Path doesn't exist. Happens at init when path is still empty string.
			self.waypoints = []
		self.duration = metadata.get(new_path, "duration")
		self.generate_graph()

	@PySide6.QtCore.Property(str, fset=set_path, notify=path_changed)
	def path(self) -> str:
		"""
		Get the currently assigned song path.
		:return: The path to the track that this item represents the waypoints of.
		"""
		return self.current_path

	def generate_graph(self) -> None:
		"""
		Re-generates the SVG data to draw.
		"""
		width = self.width()
		height = self.height()
		svg = "<svg version=\"1.0\">\n"

		nodes = []
		polyline = ""
		for timestamp, level in self.waypoints:
			if len(nodes) == 0:  # First node attaches to the left side with a horizontal line.
				polyline += f"M0,{(1 - level) * height}"
			x = width * timestamp / self.duration
			y = (1 - level) * height
			nodes.append(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"{self.node_radius}\" />\n")
			polyline += f" L{x},{y}"
		svg += f"<g stroke=\"{self.colour}\" stroke-width=\"{self.line_width}\" fill=\"{self.background_colour}\">\n"
		svg += f"<path fill=\"none\" d=\"{polyline}\" />\n"
		svg += "\n".join(nodes)
		svg += "</g>\n</svg>"

		self.svg = svg
		self.renderer = PySide6.QtSvg.QSvgRenderer(svg)
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
		pos_start = 0
		for pos_start in range(len(self.waypoints)):
			if self.waypoints[pos_start][0] > time_start:
				break  # Insert before this waypoint.

		# Test whether this waypoint is within a transition or in between transitions.
		if pos_start == 0:
			starts_within = False  # Before the first waypoint is never inside of a transition.
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
		if pos_end != 0 and self.waypoints[pos_end - 1][1] != self.waypoints[pos_end][1]:
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

		# Remove the waypoints that would get overridden.
		del self.waypoints[pos_start : pos_end]
		# Insert the new waypoints.
		self.waypoints.insert(pos_start, (time_start, level_start))
		self.waypoints.insert(pos_start + 1, (time_end, level_end))