//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15

import Lyn 1.0 as Lyn

//An invisible divider that allows resizing columns of a table.
//To use, put this element inside of the second column of the two between which you're resizing as a child element.
MouseArea {
	id: mouse_area
	width: Lyn.Theme.size["drag_handle"].width
	height: parent.height
	x: -width / 2

	property real previous_column_width
	property int previous_index

	hoverEnabled: true
	cursorShape: Qt.SizeHorCursor
	drag.target: mouse_area
	drag.axis: Drag.XAxis
	drag.minimumX: -previous_column_width + Lyn.Theme.size["table_cell_minimum"].width
	drag.maximumX: parent.width - Lyn.Theme.size["table_cell_minimum"].width - width
	drag.threshold: 0

	onXChanged: {
		const prev_width = (previous_column_width + x + width / 2) / music_table.width;
		const next_width = (parent.width - x - width / 2) / music_table.width;
		if(prev_width > 0 && next_width > 0) {
			Lyn.Preferences.set_element("directory/column_width", previous_index, prev_width);
			Lyn.Preferences.set_element("directory/column_width", previous_index + 1, next_width);
		}
		x = -width / 2;
	}
}