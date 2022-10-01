//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import "." as Widgets
import Lyn 1.0 as Lyn

/*
 * A vertical slide control, used e.g. to control volume, or other continuous one-dimensional variables.
 */
Slider {
	implicitWidth: handle.width

	value: 0.5
	from: 0
	to: 1
	orientation: Qt.Vertical
	topPadding: background_top.height / 2
	bottomPadding: background_bottom.height / 2

	//Don't use the official background since the background may contain no IDs.
	background: Item {}
	Item {
		anchors.fill: parent

		Widgets.ColourImage {
			id: background_top

			source: Lyn.Theme.icon["slider_top"]
			colour: Lyn.Theme.colour["foreground"]
		}
		Widgets.ColourImage {
			anchors {
				top: background_top.bottom
				bottom: background_bottom.top
			}

			source: Lyn.Theme.icon["slider"]
			colour: Lyn.Theme.colour["foreground"]
		}
		Widgets.ColourImage {
			id: background_bottom
			anchors.bottom: parent.bottom

			source: Lyn.Theme.icon["slider_bottom"]
			colour: Lyn.Theme.colour["foreground"]
		}
	}

	handle: Widgets.ColourImage {
		source: Lyn.Theme.icon["slider_handle"]
		colour: Lyn.Theme.colour["foreground"]

		y: parent.visualPosition * (parent.height - height - parent.topPadding - parent.bottomPadding) + parent.topPadding
	}
}