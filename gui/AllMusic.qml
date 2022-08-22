//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

import Lyn 1.0 as Lyn
import "./widgets" as Widgets

Item {
	TableView {
		anchors {
			left: parent.left
			right: parent.right
			top: header.bottom
			bottom: parent.bottom
		}

		property alias directory: music_directory.directory

		model: Lyn.MusicDirectory {
			id: music_directory

			directory: Lyn.Preferences.preferences["browse_path"]
		}
		delegate: Rectangle {
			implicitWidth: 200  //TODO: Make this resizeable.
			implicitHeight: childrenRect.height

			color: Lyn.Theme.colour[(row % 2 == 0) ? "background" : "row_alternation_background"]

			Text {
				width: parent.width

				text: display
				elide: Text.ElideRight
			}
		}
	}

	//Table header is rendered above the actual table, to prevent the need for clipping.
	Row {
		id: header
		Widgets.TableHeader {
			id: titleHeader

			text: "Title"
		}
		Widgets.TableHeader {
			id: authorHeader

			text: "Author"
		}
		Widgets.TableHeader {
			id: durationHeader

			text: "Duration"
		}
		Widgets.TableHeader {
			id: bpmHeader

			text: "BPM"
		}
		Widgets.TableHeader {
			id: commentHeader

			text: "Comment"
		}
	}
}