//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2

import "." as Widgets
import Lyn 1.0 as Lyn

/* This element is a decorative header for within a long list. */
Item {
	property alias text: title_text.text

	height: childrenRect.height

	Widgets.ColourImage {
		id: left

		source: Lyn.Theme.icon["header_left"]
		colour: Lyn.Theme.colour["lining"]
	}
	Widgets.ColourImage {
		id: right
		anchors.right: parent.right

		source: Lyn.Theme.icon["header_right"]
		colour: Lyn.Theme.colour["lining"]
	}
	Widgets.ColourImage {
		anchors.left: left.right
		anchors.right: right.left

		source: Lyn.Theme.icon["header"]
		colour: Lyn.Theme.colour["lining"]
	}

	Text {
		id: title_text
		anchors.horizontalCenter: parent.horizontalCenter

		color: Lyn.Theme.colour["foreground"]
		font: Lyn.Theme.font["header"]
	}
}