//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 6.2
import QtQuick.Controls 6.2

import Lyn 1.0 as Lyn

Button {
	width: Lyn.Theme.size["control"].width
	height: Lyn.Theme.size["control"].height

	onClicked: popup.open()

	background: Rectangle {
		color: Lyn.Theme.colour["primary"]
		border.color: Lyn.Theme.colour["lining"]
		border.width: Lyn.Theme.size["lining"].width
	}

	contentItem: Text {
		text: "Test"
		font: Lyn.Theme.font["default"]
		color: Lyn.Theme.colour["foreground"]
		horizontalAlignment: Text.AlignHCenter
		verticalAlignment: Text.AlignVCenter
		elide: Text.ElideRight
	}

	Popup {
		id: popup
		y: parent.height - Lyn.Theme.size["lining"].width
		width: parent.width
		height: width

		background: Rectangle {
			color: Lyn.Theme.colour["accent_background"]
			border.color: Lyn.Theme.colour["lining"]
			border.width: Lyn.Theme.size["lining"].width
		}

		Component {
			id: tumbler_text

			Text {
				text: modelData
				font: Lyn.Theme.font["default"]
				color: Lyn.Theme.colour["foreground"]
				horizontalAlignment: Text.AlignHCenter
				verticalAlignment: Text.AlignVCenter
			}
		}

		Component {
			id: tumbler_view

			PathView {
				id: path_view
				property real delegateHeight: parent.availableHeight / parent.visibleItemCount

				model: parent.model
				delegate: parent.delegate
				clip: true
				pathItemCount: parent.visibleItemCount + 1
				preferredHighlightBegin: 0.5
				preferredHighlightEnd: 0.5
				dragMargin: width / 2

				path: Path {
					startX: path_view.width / 2
					startY: -path_view.delegateHeight / 2

					PathLine {
						x: path_view.width / 2
						y: path_view.pathItemCount * path_view.delegateHeight - path_view.delegateHeight / 2
					}
				}

				MouseArea { //Capture scroll events in this area.
					anchors.fill: parent

					propagateComposedEvents: true

					onWheel: function(wheel) {
						if(wheel.angleDelta.y < 0) {
							path_view.incrementCurrentIndex();
						} else {
							path_view.decrementCurrentIndex();
						}
					}
				}
			}
		}

		Tumbler {
			id: hours_tumbler
			anchors {
				left: parent.left
				top: parent.top
				bottom: parent.bottom
			}
			width: parent.width / 2

			model: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
			delegate: tumbler_text

			contentItem: tumbler_view.createObject(this)
		}

		Tumbler {
			anchors {
				right: parent.right
				top: parent.top
				bottom: parent.bottom
			}
			width: parent.width / 2

			property int previousIndex: 0

			model: ["00", "05", 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
			delegate: tumbler_text
			contentItem: tumbler_view.createObject(this)

			onCurrentIndexChanged: {
				if(currentIndex == 0 && previousIndex > 6) {
					hours_tumbler.contentItem.incrementCurrentIndex();
				}
				if(currentIndex == 11 && previousIndex <= 6) {
					hours_tumbler.contentItem.decrementCurrentIndex();
				}
				previousIndex = currentIndex;
			}
		}
	}
}