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
	width: 1280
	height: 720
	visible: true
	title: "LynDJ"

	color: Lyn.Theme.colour["background"]

	Gui.TopBar {
		id: topbar
		anchors {
			top: parent.top
			left: parent.left
			right: parent.right
		}
	}

	Gui.FileBrowser {
		id: filebrowser
		anchors {
			top: topbar.bottom
			bottom: player.top
			left: parent.left
		}
		//Width to be determined by slider.
	}

	Gui.Playlist {
		anchors {
			top: topbar.bottom
			bottom: player.top
			left: filebrowser.right
			right: parent.right
		}
	}

	Gui.Player {
		id: player
		anchors {
			bottom: parent.bottom
			left: parent.left
			right: parent.right
		}
	}

	Widgets.DirectoryField {
		id: directory_field
		anchors {
			left: parent.left
			leftMargin: Lyn.Theme.size["margin"].width
			top: parent.top
			topMargin: Lyn.Theme.size["margin"].height
		}

		Component.onCompleted: currentDirectory = Lyn.Preferences.preferences["browse_path"]
		onCurrentDirectoryChanged: Lyn.Preferences.set("browse_path", currentDirectory)
	}
	Gui.AllMusic {
		anchors {
			left: parent.left
			leftMargin: Lyn.Theme.size["margin"].width
			top: directory_field.bottom
			topMargin: Lyn.Theme.size["margin"].height
		}
	}
}