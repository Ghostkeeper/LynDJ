//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2024 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

import "./widgets" as Widgets
import Lyn 1.0 as Lyn

Item {
	id: verticalDivider
	height: parent.height
	width: Lyn.Theme.size["vertical_divider"].width
	x: Lyn.Preferences.preferences["divider_pos"] * parent.width - width / 2

	property var queueButtonHandler
	property var unqueueButtonHandler
	property alias queueButtonEnabled: queue_button.enabled
	property alias unqueueButtonEnabled: unqueue_button.enabled

	Widgets.ColourImage {
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: parent.top
			bottom: queue_button.top
		}

		source: Lyn.Theme.icon["vertical_divider"]
		colour: Lyn.Theme.colour["lining"]
	}
	Widgets.ImageButton {
		id: queue_button
		anchors.horizontalCenter: parent.horizontalCenter
		y: parent.height / 4 - height

		backgroundSource: Lyn.Theme.icon["queue_background"]
		backgroundColour: Lyn.Theme.colour["lining"]
		source: Lyn.Theme.icon["queue_foreground"]
		colour: Lyn.Theme ? Lyn.Theme.colour[enabled ? (hovered ? "highlight_foreground" : "foreground") : "disabled_foreground"] : "transparent"
		onClicked: queueButtonHandler()
	}
	Widgets.ImageButton {
		id: unqueue_button
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: queue_button.bottom
		}

		backgroundSource: Lyn.Theme.icon["unqueue_background"]
		backgroundColour: Lyn.Theme.colour["lining"]
		source: Lyn.Theme.icon["unqueue_foreground"]
		colour: Lyn.Theme ? Lyn.Theme.colour[enabled ? (hovered ? "highlight_foreground" : "foreground") : "disabled_foreground"] : "transparent"
		onClicked: unqueueButtonHandler()
	}
	Widgets.ColourImage {
		id: pause_divider
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: unqueue_button.bottom
		}
		height: Lyn.Theme.size["margin"].height

		source: Lyn.Theme.icon["vertical_divider"]
		colour: Lyn.Theme.colour["lining"]
	}
	Widgets.ImageButton {
		id: pause_button
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: pause_divider.bottom
		}

		backgroundSource: Lyn.Theme.icon["pause_background"]
		backgroundColour: Lyn.Theme.colour["lining"]
		source: Lyn.Theme.icon["pause_foreground"]
		colour: Lyn.Theme ? Lyn.Theme.colour[enabled ? (hovered ? "highlight_foreground" : "foreground") : "disabled_foreground"] : "transparent"
	}
	Widgets.ColourImage {
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: pause_button.bottom
			bottom: handle.top
		}

		source: Lyn.Theme.icon["vertical_divider"]
		colour: Lyn.Theme.colour["lining"]
	}
	Widgets.ColourImage {
		id: handle
		anchors.centerIn: parent

		source: Lyn.Theme.icon["vertical_divider_handle"]
		colour: Lyn.Theme.colour["lining"]

		MouseArea { //Allow dragging.
			anchors.fill: parent

			cursorShape: Qt.SizeHorCursor

			drag.target: verticalDivider
			drag.axis: Drag.XAxis
			drag.minimumX: 0
			drag.maximumX: verticalDivider.parent.width - verticalDivider.width

			onReleased: {
				Lyn.Preferences.set("divider_pos", (verticalDivider.x + verticalDivider.width / 2) / verticalDivider.parent.width);
			}
		}
	}
	Widgets.ColourImage {
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: handle.bottom
			bottom: parent.bottom
		}

		source: Lyn.Theme.icon["vertical_divider"]
		colour: Lyn.Theme.colour["lining"]
	}
}