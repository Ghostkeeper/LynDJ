//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2
import QtQuick.Controls 6.2

import "./widgets" as Widgets
import Lyn 1.0 as Lyn

Rectangle {
	property real dividerPosition: width / 2

	height: Lyn.Theme.size["player"].height

	color: Lyn.Theme.colour["primary_background"]

	//Border extends above the player!
	Item {
		anchors {
			left: parent.left
			right: parent.right
			bottom: parent.top
			bottomMargin: -Lyn.Theme.size["border_offset"].height
		}
		height: childrenRect.height

		Widgets.ColourImage {
			id: border_left

			source: Lyn.Theme.icon["border_bottom_left"]
			colour: Lyn.Theme.colour["lining"]
		}

		Widgets.ColourImage {
			anchors {
				left: border_left.right
				right: border_middle.left
			}

			source: Lyn.Theme.icon["border_bottom"]
			colour: Lyn.Theme.colour["lining"]
		}

		Widgets.ColourImage {
			id: border_middle
			x: dividerPosition - width / 2

			source: Lyn.Theme.icon["border_bottom_middle"]
			colour: Lyn.Theme.colour["lining"]
		}

		Widgets.ColourImage {
			anchors {
				left: border_middle.right
				right: border_right.left
			}

			source: Lyn.Theme.icon["border_bottom"]
			colour: Lyn.Theme.colour["lining"]
		}

		Widgets.ColourImage {
			id: border_right
			anchors.right: parent.right

			source: Lyn.Theme.icon["border_bottom_right"]
			colour: Lyn.Theme.colour["lining"]
		}
	}

	Widgets.ImageButton {
		id: play_stop_button
		anchors {
			right: parent.right
			rightMargin: Lyn.Theme.size["margin"].width
			top: parent.top
		}

		backgroundSource: Lyn.Theme.icon[Lyn.Player.is_playing ? "stop_background" : "play_background"]
		backgroundColour: Lyn.Theme.colour["lining"]
		source: Lyn.Theme.icon[Lyn.Player.is_playing ? "stop_foreground" : "play_foreground"]
		colour: Lyn.Theme.colour[hovered ? "highlight_foreground" : "foreground"]
		onClicked: Lyn.Player.is_playing = !Lyn.Player.is_playing
	}

	Widgets.ColourImage {
		id: volume_icon
		anchors {
			left: parent.left
			leftMargin: Lyn.Theme.size["margin"].width
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
		}

		colour: Lyn.Theme.colour["foreground"]
		source: Lyn.Theme.icon["volume"]
	}
	Widgets.Slider {
		id: volume_control
		anchors {
			left: volume_icon.left
			top: volume_icon.bottom
			bottom: parent.bottom
			bottomMargin: Lyn.Theme.size["margin"].height
		}

		value: Lyn.Player.volume
		onValueChanged: Lyn.Player.volume = value
		onPressedChanged: {
			if(pressed) {
				volume_timeline.start_transition();
			} else {
				volume_timeline.end_transition(value);
			}
		}
	}

	//Containing progress indicators and Fourier image.
	Item {
		anchors {
			right: play_stop_button.left
			rightMargin: Lyn.Theme.size["margin"].width
			left: volume_control.right
			leftMargin: Lyn.Theme.size["margin"].width
			bottom: parent.bottom
			bottomMargin: Lyn.Theme.size["margin"].height
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
		}

		//Fourier image above the progress indicator.
		Widgets.ScreenImage {
			id: fourier
			anchors {
				left: parent.left
				right: parent.right
				top: parent.top
				bottom: progress_indicator.top
			}

			colour: Lyn.Theme.colour["foreground"]
			source: Lyn.Player.current_fourier
		}

		//Waypoints timeline.
		Lyn.WaypointsTimeline {
			id: volume_timeline
			anchors.fill: fourier
			path: Lyn.Player.currentPath
			field: "volume_waypoints"
		}

		//Left clip.
		Widgets.ColourImage {
			id: left_clip
			anchors {
				left: parent.left
				bottom: parent.bottom
			}
			width: Lyn.Player.current_cut_start / Lyn.Player.current_total_duration * parent.width

			colour: Lyn.Theme.colour["foreground"]
			source: Lyn.Theme.icon["clip_bar"]
		}
		Widgets.ColourImage {
			anchors {
				right: left_clip.right
				bottom: left_clip.bottom
			}

			colour: Lyn.Theme.colour["foreground"]
			source: Lyn.Theme.icon["clip_start"]
		}

		//Right clip.
		Widgets.ColourImage {
			id: right_clip
			anchors {
				right: parent.right
				bottom: parent.bottom
			}
			width: (Lyn.Player.current_total_duration - Lyn.Player.current_cut_end) / Lyn.Player.current_total_duration * parent.width

			colour: Lyn.Theme.colour["foreground"]
			source: Lyn.Theme.icon["clip_bar"]
		}
		Widgets.ColourImage {
			anchors {
				right: right_clip.left
				bottom: right_clip.bottom
			}

			colour: Lyn.Theme.colour["foreground"]
			source: Lyn.Theme.icon["clip_end"]
		}

		//Progress indicator.
		Item {
			id: progress_indicator
			anchors {
				left: left_clip.right
				right: right_clip.left
				bottom: parent.bottom
			}
			height: progress_hook.height

			Widgets.ColourImage {
				id: progress_bar
				width: 0

				colour: Lyn.Theme.colour["foreground"]
				source: Lyn.Theme.icon["progress_bar"]

				NumberAnimation on width {
					id: progress_animation
					from: 0
					to: progress_indicator.width
					duration: Lyn.Player.current_duration * 1000
					running: Lyn.Player.is_playing

					readonly property var __: Connections { //NumberAnimation cannot have child elements. Store this in a property. It still works.
						target: Lyn.Player
						function onSong_changed() {
							progress_animation.restart();
						}
						function onIs_playingChanged() {
							progress_animation.restart();
							progress_animation.running = Lyn.Player.is_playing;
						}
					}
				}
			}
			Widgets.ColourImage { //Hook at the end of the progress bar.
				id: progress_hook
				anchors.horizontalCenter: progress_bar.right

				visible: Lyn.Player.is_playing
				colour: Lyn.Theme.colour["foreground"]
				source: Lyn.Theme.icon["progress_end"]
			}
			//Progress marker overlaying the fourier timeline.
			Rectangle {
				anchors {
					horizontalCenter: progress_hook.horizontalCenter
					bottom: progress_hook.top
				}
				width: 2
				height: fourier.height

				visible: Lyn.Player.is_playing
				color: Lyn.Theme.colour["translucent_foreground"]
			}
		}

		Text
		{
			font: Lyn.Theme.font["title"]
			text: Lyn.Player.current_title
		}
	}
}