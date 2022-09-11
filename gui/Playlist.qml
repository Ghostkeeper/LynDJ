//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn
import "./widgets" as Widgets

ListView {
	id: playlist_root

	verticalLayoutDirection: ListView.BottomToTop
	clip: true
	ScrollBar.vertical: Widgets.ScrollBar {}

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
			id: mouse_area
			anchors.fill: parent

			hoverEnabled: true
			ToolTip.visible: containsMouse && !drag.active
			ToolTip.text: model.title + "<br />" + model.comment
			ToolTip.delay: 500
			drag.target: parent
			drag.axis: Drag.YAxis
			drag.minimumY: -playlist_root.contentHeight
			drag.maximumY: -parent.height
			drag.threshold: parent.height / 8

			onReleased: {
				if(drag.active) { //Was dragging.
					//Restore everything to its original position.
					const old_index = index;
					const new_index = Math.round(parent.y / -height) - 1;
					for(let i = Math.min(old_index, new_index); i <= Math.max(old_index, new_index); i++) {
						playlist_root.itemAtIndex(i).y = -parent.height * (i + 1);
					}
					playlist.reorder(model.path, new_index);
				}
			}
		}
		onYChanged: {
			//When this item is being dragged, we want to reorder it in the list.
			if(mouse_area.drag.active) {
				//Everything that we just crossed needs to be re-positioned to pretend that it already moved.
				const old_index = index;
				const new_index = Math.round(y / -height) - 1;
				if(new_index > old_index) {
					for(let i = old_index + 1; i <= new_index; i++) {
						playlist_root.itemAtIndex(i).y = -height * i;
					}
				} else if(new_index < old_index) {
					for(let i = old_index - 1; i >= new_index; i--) {
						playlist_root.itemAtIndex(i).y = -height * (i + 2);
					}
				}
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