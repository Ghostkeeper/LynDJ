# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
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

	def __init__(self, path, field, parent=None) -> None:
		"""
		Creates a timeline element that shows and interacts with the waypoints for a certain property of songs.
		:param path: The path to the song, used to reference the metadata and store any changes to the waypoints.
		:param field: The type of waypoints to show and adjust, e.g. volume, bass, mids or treble. This should be one of
		the metadata fields of the song.
		:param parent: The parent QML element to store this element under.
		"""
		super().__init__(parent)
		self.path = path
		self.field = field
		self.svg = ""
		self.renderer = None  # To be filled by the initial call to update_visualisation.
		self.duration = metadata.get(path, "duration")  # We need to know the duration of the song in order to draw the timestamps in the correct place.

		# Fill the waypoint data from the metadata of the file.
		self.waypoints = []  # List of tuples, giving first the timestamp in seconds, then the level between 0 and 1.
		waypoints_serialised = metadata.get(path, field)
		waypoints_list = waypoints_serialised.split("|")
		for waypoint_str in waypoints_list:
			waypoint_parts = waypoint_str.split(";")
			if len(waypoint_parts) != 2:  # Incorrectly formatted. Each waypoint should be 2 numbers separated by a semicolon.
				logging.warning(f"Incorrectly formatted waypoint for {path}/{field}: {waypoint_str}")
				continue  # Skip.
			try:
				timestamp = float(waypoint_parts[0])
				level = float(waypoint_parts[1])
			except ValueError:
				logging.warning(f"Incorrectly formatted float in waypoint for {path}/{field}: {waypoint_str}")
				continue  # Skip.
			self.waypoints.append((timestamp, level))
		self.generate_graph()

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