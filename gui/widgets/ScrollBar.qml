//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2022 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

import Lyn 1.0 as Lyn

/* A scrollbar that is styled for this application. */
ScrollBar
{
	implicitWidth: (size < 1.0) ? Lyn.Theme.size["scrollbar"].width : 0

	policy: (size < 1.0) ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff

	contentItem: Rectangle {
		color: Lyn.Theme.colour[parent.pressed ? "active_primary" : parent.hovered ? "highlight_primary" : "primary"]
	}
}