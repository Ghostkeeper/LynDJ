//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs

import Lyn 1.0 as Lyn
import "./widgets" as Widgets

Dialog {
	width: Lyn.Theme.size["dialogue"].width
	height: Lyn.Theme.size["dialogue"].height

	property string field //Which metadata key to change.
	property alias value: textfield.text
	property string path //Which file to change the metadata of.

	title: "Change " + field
	standardButtons: Dialog.Ok | Dialog.Cancel
	modal: true

	onOpened: {
		textfield.forceActiveFocus();
		textfield.selectAll();
	}

	Column {
		width: parent.width

		Text {
			width: parent.width

			text: "Please enter the new value for the " + field + ":"
			wrapMode: Text.Wrap
		}

		Widgets.TextField {
			id: textfield
			width: parent.width
		}
	}
}