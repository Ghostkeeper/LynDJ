//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

import Lyn 1.0 as Lyn

/*
 * Causes the image to be translucent depending on its brightness, and then recoloured in a single colour.
 */
Item {
	width: originalImage.width
	height: originalImage.height

	property alias colour: effect.colour
	property alias source: originalImage.source

	Image {
		id: originalImage
		visible: false //The actual image is hidden, so that the shader effect can still use it as source but it's not shown behind the effect.
	}

	ShaderEffect {
		id: effect
		anchors.fill: parent

		property var image: originalImage
		property color colour: "black"
		fragmentShader: "ScreenImage.frag.qsb"
	}
}