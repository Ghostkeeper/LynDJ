//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
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

	Widgets.ColourImage {
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: parent.top
			bottom: queue_button.top
		}

		source: Lyn.Theme.icon["vertical_divider"]
		colour: Lyn.Theme.colour["lining"]
	}
	Widgets.ColourImage {
		id: queue_button
		anchors.horizontalCenter: parent.horizontalCenter
		y: parent.height / 4 - height

		source: Lyn.Theme.icon["queue"]
		colour: Lyn.Theme.colour["lining"]
		MouseArea {
			anchors.fill: parent
			onClicked: queueButtonHandler()
			cursorShape: Qt.PointingHandCursor
		}
	}
	Widgets.ColourImage {
		id: unqueue_button
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: queue_button.bottom
		}

		source: Lyn.Theme.icon["unqueue"]
		colour: Lyn.Theme.colour["lining"]
		MouseArea {
			anchors.fill: parent
			cursorShape: Qt.PointingHandCursor
		}
	}
	Widgets.ColourImage {
		anchors {
			horizontalCenter: parent.horizontalCenter
			top: unqueue_button.bottom
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