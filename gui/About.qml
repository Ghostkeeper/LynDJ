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
	id: about_window
	width: Lyn.Theme.size["popup"].width
	height: Lyn.Theme.size["popup"].height
	minimumWidth: Lyn.Theme.size["popup"].width / 10

	color: Lyn.Theme.colour["background"]
	title: "About"

	ScrollView {
		id: content
		anchors.fill: parent

		rightPadding: Lyn.Theme.size["margin"].width + (ScrollBar.vertical.visible ? ScrollBar.vertical.width : 0)
		contentHeight: contentColumn.height + Lyn.Theme.size["margin"].height * 2

		ScrollBar.vertical: Widgets.ScrollBar {
			anchors.top: parent.top
			anchors.right: parent.right
			anchors.bottom: parent.bottom
		}

		Column {
			id: contentColumn
			anchors {
				top: parent.top
				topMargin: Lyn.Theme.size["margin"].height
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
			}
			width: about_window.width - Lyn.Theme.size["margin"].width - content.rightPadding

			spacing: Lyn.Theme.size["margin"].height

			Image {
				width: Lyn.Theme.size["popup"].width / 3
				height: width
				anchors.horizontalCenter: parent.horizontalCenter

				source: Lyn.Theme.icon["icon"]
			}

			Column { //Sub-column without spacing.
				anchors {
					left: parent.left
					right: parent.right
				}
				Text {
					anchors {
						left: parent.left
						right: parent.right
					}

					color: Lyn.Theme.colour["foreground"]
					font: Lyn.Theme.font["title"]
					text: "LynDJ " + Qt.application.version
					horizontalAlignment: Text.AlignHCenter
					elide: Text.ElideRight
				}
				Text {
					anchors {
						left: parent.left
						right: parent.right
					}

					color: Lyn.Theme.colour["foreground"]
					font: Lyn.Theme.font["default"]
					text: "by " + Qt.application.organization
					horizontalAlignment: Text.AlignHCenter
					elide: Text.ElideRight
				}
			}

			Text {
				anchors {
					left: parent.left
					right: parent.right
				}

				color: Lyn.Theme.colour["foreground"]
				linkColor: Lyn.Theme.colour["secondary"]
				font: Lyn.Theme.font["default"]
				wrapMode: Text.Wrap
				text: "LynDJ is distributed under the terms of the AGPLv3 license. Visit <a href=\"https://github.com/Ghostkeeper/LynDJ\">Github</a> for details on distributing the application."
				onLinkActivated: function(link) {
					Qt.openUrlExternally(link);
				}
			}

			Text {
				anchors {
					left: parent.left
					right: parent.right
				}

				color: Lyn.Theme.colour["foreground"]
				font: Lyn.Theme.font["default"]
				wrapMode: Text.Wrap
				text: "This application is free and open source, and depends on these fantastic other open source projects."
			}

			Column { //The dependencies, without spacing.
				anchors {
					left: parent.left
					leftMargin: Lyn.Theme.size["margin"].width
					right: parent.right
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://www.python.org\">Python</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Running the logic of the application"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://www.qt.io/qt-for-python\">PySide</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Showing the interface"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://github.com/irmen/pyminiaudio\">PyMiniaudio</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Decoding audio files"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://people.csail.mit.edu/hubert/pyaudio\">PyAudio</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Playing audio through the system"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://github.com/quodlibet/mutagen\">Mutagen</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Reading metadata from music tracks"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://numpy.org\">NumPy</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Processing audio data efficiently"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://scipy.org\">SciPy</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Generating audio spectrographs"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://pyinstaller.org\">PyInstaller</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Building an application executable"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://nsis.sourceforge.io\">NSIS</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Creating an installer for Windows"
					}
				}

				Item {
					anchors {
						left: parent.left
						right: parent.right
					}
					height: childrenRect.height

					Text {
						width: Math.round(parent.width * 0.3)

						elide: Text.ElideRight
						linkColor: Lyn.Theme.colour["secondary"]
						font: Lyn.Theme.font["default"]
						text: "<a href=\"https://appimage.org\">AppImageKit</a>"
						onLinkActivated: function(link) {
							Qt.openUrlExternally(link);
						}
					}
					Text {
						anchors.right: parent.right
						width: Math.round(parent.width * 0.7)

						elide: Text.ElideRight
						color: Lyn.Theme.colour["foreground"]
						font: Lyn.Theme.font["default"]
						text: "Creating an executable package for Linux"
					}
				}
			}
		}
	}
}