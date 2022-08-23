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
	Row {
		id: header
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(0)

			text: "Title"
		}
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(1)

			text: "Author"

			MouseArea {
				id: mouse_area
				width: Lyn.Theme.size["drag_handle"].width
				height: parent.height
				x: -width / 2

				hoverEnabled: true
				cursorShape: Qt.SizeHorCursor
				drag.target: mouse_area
				drag.axis: Drag.XAxis
				drag.minimumX: -100
				drag.maximumX: 100
				drag.threshold: 0

				Rectangle {
					id: handle
					anchors.fill: parent
					color: "pink"
				}
			}
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
			implicitWidth: 200 //Will be overridden by the column width provider.
			implicitHeight: Math.max(childrenRect.height, 1)

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
}