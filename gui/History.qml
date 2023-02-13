//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn
import "./widgets" as Widgets

ListView {
	id: history
	implicitHeight: Math.min(parent.height / 2, contentHeight)

	clip: true
	ScrollBar.vertical: Widgets.ScrollBar {}
	currentIndex: -1 //Start off with no items selected.

	model: Lyn.History

	delegate: Rectangle {
		width: parent ? parent.width : 0
		height: Lyn.Theme.size["card"].height

		property string path: model.path //To allow externals to see this part of the model.

		color: model.bpm
		opacity: model.suggested ? 0.5 : 1
		z: mouse_area.drag.active ? 2 : 1
		border.color: Lyn.Theme.colour["selection"]
		border.width: ListView.isCurrentItem ? Lyn.Theme.size["lining"].width : 0

		MouseArea {
			id: mouse_area
			anchors.fill: parent

			hoverEnabled: true
			ToolTip.visible: containsMouse && !drag.active
			ToolTip.text: model.title + "<br />" + model.comment
			ToolTip.delay: 500

			onClicked: {
				history.currentIndex = index;
			}
		}

		Text { //Title.
			anchors {
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
				right: duration_indicator.left
				verticalCenter: parent.verticalCenter
			}

			text: model.title
			font: Lyn.Theme.font["title"]
			elide: Text.ElideRight
		}

		Text { //Duration.
			id: duration_indicator
			anchors {
				right: parent.right
				rightMargin: Lyn.Theme.size["margin"].width
				bottom: parent.bottom
				bottomMargin: Lyn.Theme.size["margin"].height
			}

			text: model.duration
			font: Lyn.Theme.font["default"]
		}
	}

	headerPositioning: ListView.OverlayHeader
	header: Rectangle {
		anchors {
			left: parent.left
			right: parent.right
		}
		height: childrenRect.height

		color: Lyn.Theme.colour["background"]
		z: 4

		Widgets.ColourImage {
			anchors {
				left: parent.left
				right: parent.right
			}

			colour: Lyn.Theme.colour["lining"]
			source: Lyn.Theme.icon["horizontal_divider"]
		}
	}
}