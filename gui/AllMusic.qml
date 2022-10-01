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
	property string selectedFilePath: {
		if(music_table.selectedRow >= 0 && music_directory) {
			return music_directory.get_path(music_table.selectedRow);
		} else {
			return "";
		}
	}

	function selectByPath(path) {
		music_table.selectedRow = music_directory.get_row(path);
	}

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
			id: header_comment
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
		Widgets.TableHeader {
			width: music_table.columnWidthProvider(5)

			text: "Last Played"
			onWidthChanged: music_table.forceLayout()
			role: "last_played"
			table: music_table.model

			Widgets.ColumnResizer {
				previous_column_width: header_comment.width
				previous_index: 4
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
		focus: true
		model: Lyn.MusicDirectory {
			id: music_directory

			directory: Lyn.Preferences.preferences["browse_path"]
		}
		delegate: Rectangle {
			implicitWidth: 200 //Will be overridden by the column width provider.
			implicitHeight: Lyn.Theme.size["table_cell_minimum"].height

			required property bool selected

			color: Lyn.Theme.colour[row == music_table.selectedRow ? "selection" : ((row % 2 == 0) ? "background" : "accent_background")]

			Text {
				width: parent.width

				text: display
				elide: Text.ElideRight
				font: Lyn.Theme.font["default"]

				MouseArea {
					anchors.fill: parent

					acceptedButtons: Qt.LeftButton | Qt.RightButton
					hoverEnabled: parent.truncated && parent.text !== ""
					ToolTip.visible: parent.truncated && containsMouse && parent.text !== ""
					ToolTip.text: parent.text
					onClicked: function(mouse) {
						if(mouse.button === Qt.LeftButton) {
							music_table.selectedRow = row;
							music_table.focus = true;
						} else { //Right button.
							const field = music_directory.headerData(column, Qt.Horizontal, Qt.DisplayRole);
							if(field === "title" || field === "author" || field === "bpm" || field === "comment") {
								change_dialogue.field = field
								change_dialogue.path = music_directory.headerData(row, Qt.Vertical, Qt.DisplayRole);
								change_dialogue.value = display; //Put the old value in the text box.
								change_dialogue.open();
							}
						}
					}
				}
			}
		}
		ScrollBar.vertical: Widgets.ScrollBar {}
		columnWidthProvider: function(column) {
			return music_table.width * Lyn.Preferences.preferences["directory/column_width"][column];
		}

		property int _row_height: 0
		Keys.onUpPressed: if(selectedRow > 0) selectedRow--;
		Keys.onDownPressed: if(selectedRow < rows - 1) selectedRow++;
		onSelectedRowChanged: {
			//cellAtPos is deemed unreliable, probably because the table unloads cells if they are out of view and then doesn't calculate their size properly.
			//Instead we'll have to get the row height manually and calculate which parts are in view.
			if(_row_height == 0) { //The first time, store the row height.
				for(let i = 0; i < rows; ++i) {
					if(rowHeight(i) > 0) {
						_row_height = rowHeight(i);
						break;
					}
				}
			}
			if(selectedRow > 0) {
				const first_visible_row = Math.floor(contentY / _row_height);
				const last_visible_row = first_visible_row + Math.floor(height / _row_height);
				if(selectedRow <= first_visible_row) { //Selected row is above the view.
					positionViewAtRow(selectedRow, Qt.AlignTop);
				} else if(selectedRow > last_visible_row) { //Selected row is below the view.
					positionViewAtRow(selectedRow, Qt.AlignBottom);
				}
			}
		}
	}

	ChangeMetadataDialogue {
		id: change_dialogue

		onAccepted: {
			music_directory.change_metadata(path, field, value);
		}
	}
}