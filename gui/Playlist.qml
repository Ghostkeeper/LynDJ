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
	id: playlist

	verticalLayoutDirection: ListView.BottomToTop
	clip: true
	ScrollBar.vertical: Widgets.ScrollBar {}
	currentIndex: -1 //Start off with no items selected.

	model: Lyn.Playlist

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
			drag.target: ((index == 0 && Lyn.Player.is_playing) || model.suggested) ? null : parent  //The currently playing item cannot be dragged, nor suggested tracks.
			drag.axis: Drag.YAxis
			drag.minimumY: -playlist.contentHeight + (Lyn.Playlist.has_suggested_track ? parent.height : 0) //If there is a suggested track, you can't drag above it.
			drag.maximumY: -parent.height - (Lyn.Player.is_playing ? parent.height : 0)  //If playing, you can't drag items below the currently playing item.
			drag.threshold: parent.height / 8

			onReleased: {
				if(drag.active) { //Was dragging.
					//Restore everything to its original position.
					const old_index = index;
					const new_index = Math.round(parent.y / -height) - 1;
					for(let i = 0; i < playlist.count; i++) {
						if(playlist.itemAtIndex(i)) {
							playlist.itemAtIndex(i).y = -parent.height * (i + 1);
						}
					}
					if(new_index != old_index) {
						Lyn.Playlist.reorder(path, new_index);
					}
				}
			}
			onClicked: {
				playlist.currentIndex = index;
			}
		}
		onYChanged: {
			//When this item is being dragged, we want to reorder it in the list.
			if(mouse_area.drag.active) {
				playlist.currentIndex = index;

				//Everything that we just crossed needs to be re-positioned to pretend that it already moved.
				const old_index = index;
				const new_index = Math.round(y / -height) - 1;
				for(let i = 0; i < playlist.count; i++) {
					if(i != old_index && playlist.itemAtIndex(i)) {
						playlist.itemAtIndex(i).y = -height * (i + 1);
					}
				}
				if(new_index > old_index) {
					for(let i = old_index + 1; i <= new_index; i++) {
						playlist.itemAtIndex(i).y = -height * i;
					}
				} else if(new_index < old_index) {
					for(let i = old_index - 1; i >= new_index; i--) {
						playlist.itemAtIndex(i).y = -height * (i + 2);
					}
				}
			}
		}

		//Overtime indicator.
		Rectangle {
			anchors {
				top: parent.top
				right: parent.right
				left: duration_indicator.left
				leftMargin: -Lyn.Theme.size["margin"].width
			}
			visible: playlist.model.playlist_endtime() < model.cumulative_endtime
			height: {
				let endtime = playlist.model.playlist_endtime();
				let my_start = model.cumulative_endtime - model.duration_seconds;
				if(endtime < my_start) return parent.height; //Also before start, so this complete track is over time.
				let fraction = 1 - (endtime - my_start) / model.duration_seconds;
				return parent.height * fraction;
			}

			color: Lyn.Theme.colour["warning"]
		}

		Widgets.ImageButton { //Add to queue if suggested by AutoDJ.
			id: add_from_autodj
			anchors {
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
				top: parent.top
				topMargin: Lyn.Theme.size["margin"].height
				bottom: parent.bottom
				bottomMargin: Lyn.Theme.size["margin"].height
			}
			width: height

			visible: model.suggested
			source: Lyn.Theme.icon["plus"]
			colour: Lyn.Theme.colour["foreground"]
			onClicked: Lyn.Playlist.add(model.path)
		}

		Text { //Title.
			anchors {
				left: add_from_autodj.visible ? add_from_autodj.right : parent.left
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