//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

import "." as Gui
import "./widgets" as Widgets
import Lyn 1.0 as Lyn

Item {
	property alias selectedFilePath: all_music.selectedFilePath

	function selectByPath(path) {
		all_music.selectByPath(path);
	}

	Widgets.DirectoryField {
		id: directory_field
		anchors {
			left: parent.left
			right: parent.right
			top: parent.top
		}

		Component.onCompleted: currentDirectory = Lyn.Preferences.preferences["directory/browse_path"]
		onCurrentDirectoryChanged: Lyn.Preferences.set("directory/browse_path", currentDirectory)
	}
	Gui.AllMusic {
		id: all_music
		anchors {
			left: parent.left
			right: parent.right
			top: directory_field.bottom
			topMargin: Lyn.Theme.size["margin"].height
			bottom: parent.bottom
		}
	}
}