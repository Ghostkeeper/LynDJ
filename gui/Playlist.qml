//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn

ListView {
	verticalLayoutDirection: ListView.BottomToTop

	function add(path) {
		playlist.add(path);
	}

	model: Lyn.Playlist {
		id: playlist
	}

	delegate: Rectangle {
		width: parent.width
		height: Lyn.Theme.size["card"].height

		color: model.bpm

		MouseArea {
			anchors.fill: parent

			hoverEnabled: true
			ToolTip.visible: containsMouse
			ToolTip.text: model.title + "<br />" + model.comment
			ToolTip.delay: 500
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

		Text { //Cumulative duration.
			anchors {
				right: parent.right
				rightMargin: Lyn.Theme.size["margin"].width
				top: parent.top
			}

			text: model.cumulative_duration
			font: Lyn.Theme.font["detail"]
		}
	}
}