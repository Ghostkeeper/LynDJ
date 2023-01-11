//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import "./widgets" as Widgets
import Lyn 1.0 as Lyn

Rectangle {
	property real dividerPosition: width / 2

	height: Lyn.Theme.size["topbar"].height

	color: Lyn.Theme.colour["primary_background"]

	Image {
		id: logo
		anchors {
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
			left: parent.left
			leftMargin: Lyn.Theme.size["margin"].width
			bottom: parent.bottom
			bottomMargin: Lyn.Theme.size["margin"].height
		}
		width: height

		source: Lyn.Theme.icon["icon"]
		sourceSize.width: width
		sourceSize.height: height
	}

	Text {
		anchors {
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
			left: logo.right
			leftMargin: Lyn.Theme.size["margin"].width
			bottom: parent.bottom
			bottomMargin: Lyn.Theme.size["margin"].height
			right: button_row.left
			rightMargin: Lyn.Theme.size["margin"].width
		}

		text: "LynDJ"
		font: Lyn.Theme.font["title"]
		color: Lyn.Theme.colour["foreground"]
		verticalAlignment: Text.AlignVCenter
		elide: Text.AlignRight
	}

	//Row of buttons on the top right.
	Row {
		id: button_row
		anchors {
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
			right: parent.right
			rightMargin: Lyn.Theme.size["margin"].width
			bottom: parent.bottom
			bottomMargin: Lyn.Theme.size["margin"].height
		}

		spacing: Lyn.Theme.size["margin"].width

		MouseArea {
			height: parent.height
			width: childrenRect.width

			visible: Lyn.BackgroundTasks.progress != 1.0 //Only visible if there is something processing.
			hoverEnabled: visible
			ToolTip.visible: visible && containsMouse
			ToolTip.text: "Background tasks: " + Lyn.BackgroundTasks.numDone + " / " + Lyn.BackgroundTasks.numTotal + " (" + Lyn.BackgroundTasks.currentDescription + ")"

			Widgets.ColourImage {
				id: processing_icon
				height: parent.height - Lyn.Theme.size["margin"].height - progress_bar.height
				width: height

				source: Lyn.Theme.icon["processing"]
				colour: Lyn.Theme.colour["foreground"]
			}

			ProgressBar {
				id: progress_bar
				anchors.top: processing_icon.bottom
				anchors.topMargin: Lyn.Theme.size["margin"].height
				width: processing_icon.width
				height: Lyn.Theme.size["lining"].height

				value: Lyn.BackgroundTasks.progress
				background: Item {} //No background.
				contentItem: Rectangle {
					width: progress_bar.visualPosition * progress_bar.width
					height: progress_bar.height
					color: Lyn.Theme.colour["foreground"]
				}
			}
		}

		//Mono/stereo toggle.
		Widgets.ImageButton {
			height: parent.height
			width: height

			source: Lyn.Theme.icon[Lyn.Player.mono ? "mono" : "stereo"]
			colour: Lyn.Theme.colour["foreground"]
			onClicked: Lyn.Player.mono = !Lyn.Player.mono
			ToolTip.text: Lyn.Player.mono ? "Mono" : "Stereo"
		}

		//Preferences screen.
		Widgets.ImageButton {
			height: parent.height
			width: height

			source: Lyn.Theme.icon["preferences"]
			colour: Lyn.Theme.colour["foreground"]
			onClicked: preferences.show()

			Preferences {
				id: preferences
			}
		}
	}

	//Border extends below the actual size of the top bar!
	Item {
		anchors {
			left: parent.left
			right: parent.right
			top: parent.bottom
			topMargin: -Lyn.Theme.size["border_offset"].height
		}

		Widgets.ColourImage {
			id: border_left

			source: Lyn.Theme.icon["border_top_left"]
			colour: Lyn.Theme.colour["lining"]
		}
		Widgets.ColourImage {
			anchors {
				left: border_left.right
				right: border_middle.left
			}

			source: Lyn.Theme.icon["border_top"]
			colour: Lyn.Theme.colour["lining"]
		}
		Widgets.ColourImage {
			id: border_middle
			x: dividerPosition - width / 2

			source: Lyn.Theme.icon["border_top_middle"]
			colour: Lyn.Theme.colour["lining"]
		}
		Widgets.ColourImage {
			anchors {
				left: border_middle.right
				right: border_right.left
			}

			source: Lyn.Theme.icon["border_top"]
			colour: Lyn.Theme.colour["lining"]
		}
		Widgets.ColourImage {
			id: border_right
			anchors.right: parent.right

			source: Lyn.Theme.icon["border_top_right"]
			colour: Lyn.Theme.colour["lining"]
		}
	}
}