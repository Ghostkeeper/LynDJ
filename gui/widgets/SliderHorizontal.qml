//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import "." as Widgets
import Lyn 1.0 as Lyn

/*
 * A horizontal slide control, used e.g. to control a numerical setting, or other continuous one-dimensional variables.
 */
Slider {
	implicitWidth: handle.width
	width: Lyn.Theme.size["control"].width
	height: Lyn.Theme.size["control"].height

	value: 0.5
	from: 0
	to: 1
	orientation: Qt.Horizontal
	leftPadding: background_left.height / 2
	rightPadding: background_right.height / 2

	//Don't use the official background since the background may contain no IDs.
	background: Item {}
	Item {
		anchors.fill: parent

		Widgets.ColourImage {
			id: background_left

			source: Lyn.Theme.icon["slider_left"]
			colour: Lyn.Theme.colour["foreground"]
		}
		Widgets.ColourImage {
			anchors {
				left: background_left.right
				right: background_right.left
			}

			source: Lyn.Theme.icon["slider_horizontal"]
			colour: Lyn.Theme.colour["foreground"]
		}
		Widgets.ColourImage {
			id: background_right
			anchors.right: parent.right

			source: Lyn.Theme.icon["slider_right"]
			colour: Lyn.Theme.colour["foreground"]
		}
	}

	handle: Widgets.ColourImage {
		source: Lyn.Theme.icon["slider_horizontal_handle"]
		colour: Lyn.Theme.colour["foreground"]

		x: parent.visualPosition * (parent.width - width - parent.leftPadding - parent.rightPadding) + parent.leftPadding
	}
}