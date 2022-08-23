//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn
import "./widgets" as Widgets

Item {
	TableView {
		id: music_table
		anchors {
			left: parent.left
			right: parent.right
			top: header.bottom
			bottom: parent.bottom
		}
		onWidthChanged: forceLayout() //Re-calculate column widths.

		flickableDirection: Flickable.VerticalFlick
		clip: true
		model: Lyn.MusicDirectory {
			id: music_directory

			directory: Lyn.Preferences.preferences["browse_path"]
		}
		delegate: Rectangle {
			implicitWidth: music_table.columnWidthProvider()
			implicitHeight: childrenRect.height

			color: Lyn.Theme.colour[(row % 2 == 0) ? "background" : "row_alternation_background"]

			Text {
				width: parent.width

				text: display
				elide: Text.ElideRight
			}
		}
		ScrollBar.vertical: Widgets.ScrollBar {}
		columnWidthProvider: function(column) {
			return music_table.width * Lyn.Preferences.preferences["directory/column_width"][column];
		}
	}

	Row {
		id: header
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(0)

			text: "Title"
		}
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(1)

			text: "Author"
		}
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(2)

			text: "Duration"
		}
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(3)

			text: "BPM"
		}
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(4)

			text: "Comment"
		}
	}
}