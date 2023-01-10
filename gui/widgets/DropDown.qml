//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2
import QtQuick.Controls 6.2

import "." as Widgets
import Lyn 1.0 as Lyn

ComboBox {
	id: combo_box
	width: Lyn.Theme.size["control"].width
	height: Lyn.Theme.size["control"].height

	background: Rectangle {
		anchors.fill: parent

		color: Lyn.Theme.colour["primary"]
	}

	contentItem: Text {
		anchors {
			left: parent.left
			leftMargin: Lyn.Theme.size["margin"].width
			right: parent.indicator.left
			rightMargin: Lyn.Theme.size["margin"].width
		}

		text: parent.displayText
		font: Lyn.Theme.font["default"]
		color: Lyn.Theme.colour["foreground"]
		verticalAlignment: Text.AlignVCenter
		elide: Text.ElideRight
	}

	indicator: ColourImage {
		anchors {
			verticalCenter: parent.verticalCenter
			right: parent.right
			rightMargin: Lyn.Theme.size["margin"].width
		}

		source: Lyn.Theme.icon["chevron"]
		colour: Lyn.Theme.colour["foreground"]
	}

	popup: Popup {
		y: parent.height
		width: parent.width

		padding: 0

		background: Rectangle {
			color: Lyn.Theme.colour["accent_background"]
		}

		contentItem: ListView {
			implicitHeight: contentHeight

			clip: true
			model: parent.visible ? combo_box.delegateModel : null
			currentIndex: combo_box.highlightedIndex

			//ScrollBar.vertical: Widgets.ScrollBar {}
		}
	}

	delegate: ItemDelegate {
		width: combo_box.width
		height: Lyn.Theme.size["control"].height

		highlighted: combo_box.highlightedIndex === index
		padding: Lyn.Theme.size["margin"].width

		contentItem: Text {
			text: combo_box.textRole ? (Array.isArray(combo_box.model) ? modelData[combo_box.textRole] : model[combo_box.textRole]) : modelData
			color: Lyn.Theme.colour["foreground"]
			font: Lyn.Theme.font["default"]
			elide: Text.ElideRight
			verticalAlignment: Text.AlignVCenter
		}

		background: Rectangle {
			color: parent.highlighted ? Lyn.Theme.colour["active_primary"] : Lyn.Theme.colour["accent_background"]
		}
	}

	states: [
		State {
			name: "hovered"
			when: hovered && !pressed && !popup.opened
			PropertyChanges {
				target: background
				color: Lyn.Theme.colour["highlight_primary"]
			}
		},
		State {
			name: "pressed"
			when: pressed || popup.opened
			PropertyChanges {
				target: background
				color: Lyn.Theme.colour["active_primary"]
			}
		}
	]
}