//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn

Button {
	width: Lyn.Theme.size["button"].width
	height: Lyn.Theme.size["button"].height

	font: Lyn.Theme.font["default"]
	flat: true
	ToolTip.text: text
	ToolTip.visible: label.truncated && hovered

	background: Rectangle {
		anchors.fill: parent

		color: Lyn.Theme.colour["primary"]
	}

	contentItem: Text {
		id: label
		anchors.fill: parent

		text: parent.text
		font: parent.font
		color: Lyn.Theme.colour["foreground"]
		elide: Text.ElideRight
		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
	}

	states: [
		State {
			name: "hovered"
			when: hovered && !pressed
			PropertyChanges {
				target: background
				color: Lyn.Theme.colour["highlight_primary"]
			}
		},
		State {
			name: "pressed"
			when: pressed
			PropertyChanges {
				target: background
				color: Lyn.Theme.colour["active_primary"]
			}
		}
	]
}