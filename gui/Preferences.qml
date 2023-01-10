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
	id: preferences_window
	width: Lyn.Theme.size["popup"].width
	height: Lyn.Theme.size["popup"].height

	color: Lyn.Theme.colour["background"]
	title: "Preferences"

	ScrollView {
		id: content
		anchors.fill: parent

		ScrollBar.vertical: Widgets.ScrollBar {
			anchors.top: parent.top
			anchors.right: parent.right
			anchors.bottom: parent.bottom
		}

		Column {
			anchors {
				top: parent.top
				topMargin: Lyn.Theme.size["margin"].height
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
			}
			width: preferences_window.width - Lyn.Theme.size["margin"].width * 2

			spacing: Lyn.Theme.size["margin"].height

			Widgets.Header {
				width: parent.width

				text: "General"
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.DropDown {
					id: testField
					anchors.right: parent.right

					model: Lyn.Theme.theme_names
					currentIndex: model.indexOf(Lyn.Preferences.preferences["theme"])
					onCurrentIndexChanged: {
						Lyn.Preferences.set("theme", model[currentIndex])
					}
				}
				Text {
					anchors.verticalCenter: testField.verticalCenter
					text: "Theme"
				}
			}
		}
	}
}