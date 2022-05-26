//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn

TextField {
	width: Lyn.Theme.size["control"].width
	height: Lyn.Theme.size["control"].height

	color: Lyn.Theme.colour[enabled ? "foreground": "disabled_foreground"]
	font: Lyn.Theme.font["default"]

	background: Rectangle {
		anchors.fill: parent

		color: Lyn.Theme.colour[enabled ? "background" : "disabled_background"]
		border.width: Lyn.Theme.size["lining"].width
		border.color: Lyn.Theme.colour["lining"]
	}
}