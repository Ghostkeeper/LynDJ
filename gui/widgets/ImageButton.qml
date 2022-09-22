//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import "." as Widgets

Button {
	id: image_button
	width: background_image.width
	height: background_image.height

	property alias source: background_image.source
	property alias colour: background_image.colour

	background: Item {} //No background. Just foreground.

	Widgets.ColourImage {
		id: background_image
	}

	MouseArea { //To change the cursor.
		anchors.fill: parent

		onPressed: function(mouse) { //Don't catch the mouse events.
			mouse.accepted = false;
		}
		cursorShape: Qt.PointingHandCursor
		enabled: parent.enabled
	}
}