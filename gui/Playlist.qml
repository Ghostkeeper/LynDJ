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

		MouseArea {
			anchors.fill: parent

			hoverEnabled: true
			ToolTip.visible: containsMouse
			ToolTip.text: model.title + "<br />" + model.comment
			ToolTip.delay: 500
		}

		Text {
			anchors {
				left: parent.left
				right: duration_indicator.left
				verticalCenter: parent.verticalCenter
			}

			text: model.title
			font: Lyn.Theme.font["title"]
			elide: Text.ElideRight
		}

		Text {
			id: duration_indicator
			anchors {
				right: parent.right
				bottom: parent.bottom
			}

			text: model.duration
			font: Lyn.Theme.font["default"]
		}
	}
}