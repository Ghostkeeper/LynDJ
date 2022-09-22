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
	width: foreground_image.width
	height: foreground_image.height

	property alias backgroundSource: background_image.source
	property alias backgroundColour: background_image.colour
	property alias source: foreground_image.source
	property alias colour: foreground_image.colour

	background: Item {} //Can't use IDs in the background, which we do need for the alias. So we make our own background manually.

	Widgets.ColourImage {
		id: background_image
	}

	Widgets.ColourImage {
		id: foreground_image
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