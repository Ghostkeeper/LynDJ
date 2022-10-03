# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import PySide6.QtQuick

import theme

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