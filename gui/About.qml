//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2
import QtQuick.Controls 6.2

import "./widgets" as Widgets
import Lyn 1.0 as Lyn

Window {
	id: about_window
	width: Lyn.Theme.size["popup"].width
	height: Lyn.Theme.size["popup"].height

	color: Lyn.Theme.colour["background"]
	title: "About"

	ScrollView {
		id: content
		anchors.fill: parent

		rightPadding: Lyn.Theme.size["margin"].width + (ScrollBar.vertical.visible ? ScrollBar.vertical.width : 0)
		contentHeight: contentColumn.height + Lyn.Theme.size["margin"].height * 2

		ScrollBar.vertical: Widgets.ScrollBar {
			anchors.top: parent.top
			anchors.right: parent.right
			anchors.bottom: parent.bottom
		}

		Column {
			id: contentColumn
			anchors {
				top: parent.top
				topMargin: Lyn.Theme.size["margin"].height
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
			}
			width: about_window.width - Lyn.Theme.size["margin"].width - content.rightPadding

			spacing: Lyn.Theme.size["margin"].height

			Image {
				width: parent.width / 3
				height: width
				anchors.horizontalCenter: parent.horizontalCenter

				source: Lyn.Theme.icon["icon"]
			}
		}
	}
}