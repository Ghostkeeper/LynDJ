//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2
import QtQuick.Controls 6.2

import Lyn 1.0 as Lyn

SpinBox {
	id: spin_box
	width: Lyn.Theme.size["control"].width
	height: Lyn.Theme.size["control"].height

	editable: true

	background: Rectangle {
		anchors.fill: parent

		color: Lyn.Theme.colour["background"]
	}

	contentItem: TextInput {
		text: spin_box.textFromValue(spin_box.value, spin_box.locale)
		font: Lyn.Theme.font["default"]
		color: Lyn.Theme.colour["foreground"]
		horizontalAlignment: Qt.AlignHCenter
		verticalAlignment: Qt.AlignVCenter
		validator: spin_box.validator
	}

	up.indicator: Rectangle {
		anchors.right: parent.right
		height: parent.height
		width: height

		color: Lyn.Theme.colour[spin_box.up.pressed ? "active_primary" : (spin_box.up.hovered ? "highlight_primary" : "primary")]

		Text {
			anchors.fill: parent

			text: "+"
			font: Lyn.Theme.font["default"]
			color: Lyn.Theme.colour["foreground"]
			horizontalAlignment: Text.AlignHCenter
			verticalAlignment: Text.AlignVCenter
		}
	}

	down.indicator: Rectangle {
		height: parent.height
		width: height

		color: Lyn.Theme.colour[spin_box.down.pressed ? "active_primary" : (spin_box.down.hovered ? "highlight_primary" : "primary")]

		Text {
			anchors.fill: parent

			text: "-"
			font: Lyn.Theme.font["default"]
			color: Lyn.Theme.colour["foreground"]
			horizontalAlignment: Text.AlignHCenter
			verticalAlignment: Text.AlignVCenter
		}
	}
}