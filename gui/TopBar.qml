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

	//Row of controls on the top right.
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

		Text {
			height: parent.height

			visible: Lyn.Preferences.preferences["autodj/enabled"]
			text: "AutoDJ energy:"
			font: Lyn.Theme.font["default"]
			color: Lyn.Theme.colour["foreground"]
			verticalAlignment: Text.AlignVCenter
		}

		Row { //For the AutoDJ energy slider.
			visible: Lyn.Preferences.preferences["autodj/enabled"]

			Widgets.ColourImage {
				source: Lyn.Theme.icon["low_energy"]
				colour: Lyn.Theme.colour["foreground"]
			}

			Widgets.SliderHorizontal {
				value: Lyn.Preferences.preferences["autodj/energy"]
				from: 0
				to: 100
				onMoved: Lyn.Preferences.set("autodj/energy", value)
			}

			Widgets.ColourImage {
				source: Lyn.Theme.icon["high_energy"]
				colour: Lyn.Theme.colour["foreground"]
			}
		}

		Widgets.ColourImage {
			visible: Lyn.Preferences.preferences["autodj/enabled"]
			source: Lyn.Theme.icon["top_bar_divider"]
			colour: Lyn.Theme.colour["lining"]
		}

		Text {
			height: parent.height

			text: "End time:"
			font: Lyn.Theme.font["default"]
			color: Lyn.Theme.colour["foreground"]
			verticalAlignment: Text.AlignVCenter
		}

		Widgets.TimeSelector {
			property bool time_is_set: false //Only watch for time changes when we've already set it from the preferences.
			Component.onCompleted: {
				set_time(Lyn.Preferences.preferences["playlist/end_time"]);
				time_is_set = true;
			}
			onTimeChanged: {
				if(time_is_set) {
					Lyn.Preferences.set("playlist/end_time", time);
				}
			}
		}

		Widgets.ColourImage {
			source: Lyn.Theme.icon["top_bar_divider"]
			colour: Lyn.Theme.colour["lining"]
		}

		MouseArea {
			height: parent.height
			width: childrenRect.width

			visible: Lyn.BackgroundTasks.progress != 1.0 //Only visible if there is something processing.
			hoverEnabled: visible
			ToolTip.visible: visible && containsMouse
			ToolTip.text: "Background tasks: " + Lyn.BackgroundTasks.num_done + " / " + Lyn.BackgroundTasks.num_total + " (" + Lyn.BackgroundTasks.current_description + ")"

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