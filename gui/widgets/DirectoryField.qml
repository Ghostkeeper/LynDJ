//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs

import Lyn 1.0 as Lyn
import "." as Widgets

Item {
	id: directory_field
	width: Lyn.Theme.size["control"].width
	height: childrenRect.height

	property alias currentDirectory: directory.text

	Widgets.Button {
		id: browseButton
		anchors.right: parent.right

		text: "Browse..."

		onClicked: browseDialog.open()
	}

	Widgets.TextField {
		id: directory
		anchors {
			left: parent.left
			right: browseButton.left
		}
	}

	FolderDialog {
		id: browseDialog

		currentFolder: "file:\/\/" + directory_field.currentDirectory
		acceptLabel: "Select"

		onAccepted: {
			var path = selectedFolder.toString();
			if(path.startsWith("file:///")) {
				//On Windows, the path starts with file:///c:/[...] and should be turned into c:/[...]
				//However on Unix, the path starts with file:///home/[...] and should be turned into /home/[...]
				//So on Windows, one extra slash needs to be removed. Detect that it's Windows by having a drive letter there.
				var schema_length = path.charAt(9) === ":" ? 8 : 7;
				path = path.substring(schema_length);
			}
			path = decodeURIComponent(path); //Unescape HTML-encoded characters.
			directory.text = path;
		}
	}
}