//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import "./widgets" as Widgets
import "." as Gui
import Lyn 1.0 as Lyn

ApplicationWindow {
	//Position and size will be overridden with the preferences on completing the load.
	x: 100
	y: 100
	width: 1280
	height: 720

	title: "LynDJ"

	color: Lyn.Theme.colour["background"]

	Component.onCompleted: {
		x = Lyn.Preferences.preferences["window/x"];
		y = Lyn.Preferences.preferences["window/y"];
		width = Lyn.Preferences.preferences["window/width"];
		height = Lyn.Preferences.preferences["window/height"];
		switch(Lyn.Preferences.preferences["window/visibility"]) {
			default:
			case "windowed": showNormal(); break;
			case "maximised": showMaximized(); break;
			case "fullscreen": showFullScreen(); break;
		}
	}
	onXChanged: function(x) {
		if(visibility == Window.Windowed) {
			Lyn.Preferences.set("window/x", x);
		}
	}
	onYChanged: function(y) {
		if(visibility == Window.Windowed) {
			Lyn.Preferences.set("window/y", y);
		}
	}
	onWidthChanged: function(width) {
		if(visibility == Window.Windowed) {
			Lyn.Preferences.set("window/width", width);
		}
	}
	onHeightChanged: function(height) {
		if(visibility == Window.Windowed) {
			Lyn.Preferences.set("window/height", height);
		}
	}
	onVisibilityChanged: function(visibility) {
		switch(visibility) {
			default:
			case Window.Minimized:
			case Window.Hidden:
				break;
			case Window.Windowed: //Only store position/size in windowed mode.
				Lyn.Preferences.set("window/visibility", "windowed");
				x = Lyn.Preferences.preferences["window/x"];
				y = Lyn.Preferences.preferences["window/y"];
				width = Lyn.Preferences.preferences["window/width"];
				height = Lyn.Preferences.preferences["window/height"];
				break;
			case Window.FullScreen: Lyn.Preferences.set("window/visibility", "fullscreen"); break;
			case Window.Maximized: Lyn.Preferences.set("window/visibility", "maximised"); break;
		}
	}
	onClosing: {
		Lyn.Application.closing();
	}

	Item {
		anchors {
			top: topbar.bottom
			topMargin: Lyn.Theme.size["border_width"].height - Lyn.Theme.size["border_offset"].height
			bottom: player.top
			bottomMargin: Lyn.Theme.size["border_width"].height - Lyn.Theme.size["border_offset"].height
			left: parent.left
			right: parent.right
		}

		Gui.FileBrowser {
			id: file_browser
			anchors {
				top: parent.top
				bottom: parent.bottom
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
				right: vertical_divider.left
			}
			//Width to be determined by slider.
		}

		Gui.Playlist {
			id: playlist
			anchors {
				top: parent.top
				bottom: history.top
				left: vertical_divider.right
				right: parent.right
				rightMargin: Lyn.Theme.size["margin"].width
			}
			onCurrentIndexChanged: {
				if(currentItem) {
					history.currentIndex = -1;
					file_browser.selectByPath(currentItem.path);
				}
			}
		}

		Gui.History {
			id: history
			anchors {
				bottom: parent.bottom
				left: vertical_divider.right
				right: parent.right
				rightMargin: Lyn.Theme.size["margin"].width
			}
			height: 0

			onImplicitHeightChanged: {
				if(height > 0) {
					height = implicitHeight;
				}
			}

			Behavior on height {
				PropertyAnimation {
					duration: 500
					easing.type: Easing.InOutQuad
				}
			}
			onCurrentIndexChanged: {
				if(currentItem) {
					playlist.currentIndex = -1;
					file_browser.selectByPath(currentItem.path);
				}
			}
		}

		Rectangle {
			anchors {
				horizontalCenter: playlist.horizontalCenter
				bottom: history.top
				bottomMargin: -Lyn.Theme.size["border_offset"].height
			}
			width: childrenRect.width
			height: childrenRect.height

			color: Lyn.Theme.colour["background"]

			Widgets.ImageButton {
				source: Lyn.Theme.icon[history.height === 0 ? "expando_up" : "expando_down"]
				colour: Lyn.Theme.colour["lining"]
				onClicked: {
					if(history.height === history.implicitHeight) {
						history.height = 0;
					} else {
						history.height = history.implicitHeight;
					}
				}
				ToolTip.text: history.height === 0 ? "Show history" : "Hide history"
				ToolTip.delay: 500
			}
		}

		Gui.VerticalDivider {
			id: vertical_divider

			queueButtonHandler: function() {
				if(file_browser.selectedFilePath !== "") {
					Lyn.Playlist.add(file_browser.selectedFilePath);
				}
			}
			unqueueButtonHandler: function() {
				if(playlist.currentIndex != -1) {
					Lyn.Playlist.remove(playlist.currentIndex);
				}
			}
			queueButtonEnabled: file_browser.selectedFilePath !== ""
			unqueueButtonEnabled: playlist.currentIndex != -1 && !(playlist.currentIndex == 0 && Lyn.Player.isPlaying) && !(playlist.currentIndex == playlist.count - 1 && Lyn.Playlist.has_suggested_track)
		}
	}

	Gui.TopBar {
		id: topbar
		anchors {
			top: parent.top
			left: parent.left
			right: parent.right
		}

		dividerPosition: vertical_divider.x + vertical_divider.width / 2
	}

	Gui.Player {
		id: player
		anchors {
			bottom: parent.bottom
			left: parent.left
			right: parent.right
		}

		dividerPosition: topbar.dividerPosition
	}
}