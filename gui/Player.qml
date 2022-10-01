//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

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

		backgroundSource: Lyn.Theme.icon[Lyn.Player.isPlaying ? "stop_background" : "play_background"]
		backgroundColour: Lyn.Theme.colour["lining"]
		source: Lyn.Theme.icon[Lyn.Player.isPlaying ? "stop_foreground" : "play_foreground"]
		colour: Lyn.Theme.colour[hovered ? "highlight_foreground" : "foreground"]
		onClicked: Lyn.Player.isPlaying = !Lyn.Player.isPlaying
	}
	Widgets.ScreenImage {
		id: timeline
		anchors {
			right: play_stop_button.left
			rightMargin: Lyn.Theme.size["margin"].width
			left: parent.left
			leftMargin: Lyn.Theme.size["margin"].width
			bottom: parent.bottom
			bottomMargin: Lyn.Theme.size["margin"].height
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
		}

		colour: Lyn.Theme.colour["foreground"]
		source: Lyn.Player.currentFourier
	}
}