//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

import Lyn 1.0 as Lyn

Rectangle {
	height: Lyn.Theme.size["topbar"].height

	color: Lyn.Theme.colour["primary_background"]

	//Border extends below the actual size of the top bar!
	Item {
		anchors {
			left: parent.left
			right: parent.right
			top: parent.bottom
		}
		height: Lyn.Theme.size["margin"].height

		Image {
			id: border_left
			height: parent.height

			source: Lyn.Theme.icon["border_top_left"]
		}
		Image {
			id: border_middle
			anchors {
				left: border_left.right
				right: border_right.left
			}
			height: parent.height

			source: Lyn.Theme.icon["border_top"]
		}
		Image {
			id: border_right
			anchors.right: parent.right
			height: parent.height

			source: Lyn.Theme.icon["border_top_right"]
		}
	}
}