//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2
import QtQuick.Controls 6.2

import Lyn 1.0 as Lyn
import "./widgets" as Widgets

Item {
	Row {
		id: header
		Widgets.TableHeader {
			id: header_title
			width: music_table.columnWidthProvider(0)

			text: "Title"
			onWidthChanged: music_table.forceLayout()
			role: "title"
			table: music_table.model
		}
		Widgets.TableHeader {
			id: header_author
			width: music_table.columnWidthProvider(1)

			text: "Author"
			onWidthChanged: music_table.forceLayout()
			role: "author"
			table: music_table.model

			Widgets.ColumnResizer {
				previous_column_width: header_title.width
				previous_index: 0
			}
		}
		Widgets.TableHeader {
			id: header_duration
			width: music_table.columnWidthProvider(2)

			text: "Duration"
			onWidthChanged: music_table.forceLayout()
			role: "duration"
			table: music_table.model

			Widgets.ColumnResizer {
				previous_column_width: header_author.width
				previous_index: 1
			}
		}
		Widgets.TableHeader {
			id: header_bpm
			width: music_table.columnWidthProvider(3)

			text: "BPM"
			onWidthChanged: music_table.forceLayout()
			role: "bpm"
			table: music_table.model

			Widgets.ColumnResizer {
				previous_column_width: header_duration.width
				previous_index: 2
			}
		}
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(4)

			text: "Comment"
			onWidthChanged: music_table.forceLayout()
			role: "comment"
			table: music_table.model

			Widgets.ColumnResizer {
				previous_column_width: header_bpm.width
				previous_index: 3
			}
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

		property int selectedRow: -1

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

			required property bool selected

			color: Lyn.Theme.colour[row == music_table.selectedRow ? "selection" : ((row % 2 == 0) ? "background" : "row_alternation_background")]

			Text {
				width: parent.width

				text: display
				elide: Text.ElideRight
				font: Lyn.Theme.font["default"]

				MouseArea {
					anchors.fill: parent

					hoverEnabled: parent.truncated && parent.text !== ""
					ToolTip.visible: parent.truncated && containsMouse && parent.text !== ""
					ToolTip.text: parent.text
					onClicked: { music_table.selectedRow = row; }
				}
			}
		}
		ScrollBar.vertical: Widgets.ScrollBar {}
		columnWidthProvider: function(column) {
			return music_table.width * Lyn.Preferences.preferences["directory/column_width"][column];
		}
	}
}