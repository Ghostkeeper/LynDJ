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
	id: preferences_window
	width: Lyn.Theme.size["popup"].width
	height: Lyn.Theme.size["popup"].height

	color: Lyn.Theme.colour["background"]
	title: "Preferences"

	ScrollView {
		id: content
		anchors.fill: parent

		ScrollBar.vertical: Widgets.ScrollBar {
			anchors.top: parent.top
			anchors.right: parent.right
			anchors.bottom: parent.bottom
		}

		Column {
			anchors {
				top: parent.top
				topMargin: Lyn.Theme.size["margin"].height
				left: parent.left
				leftMargin: Lyn.Theme.size["margin"].width
			}
			width: preferences_window.width - Lyn.Theme.size["margin"].width * 2

			spacing: Lyn.Theme.size["margin"].height

			Widgets.Header {
				width: parent.width

				text: "Interface"
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.DropDown {
					id: theme_selector
					anchors.right: parent.right

					model: Lyn.Theme.theme_names
					currentIndex: model.indexOf(Lyn.Preferences.preferences["theme"])
					onActivated: function(index) {
						Lyn.Preferences.set("theme", model[index])
					}
				}
				Text {
					anchors.verticalCenter: theme_selector.verticalCenter

					text: "Theme"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: fourier_width
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["player/fourier_samples"]
					from: 16
					to: 16384
					stepSize: 256
					onValueModified: Lyn.Preferences.set("player/fourier_samples", value)
				}
				Text {
					anchors.verticalCenter: fourier_width.verticalCenter

					text: "Fourier time resolution"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
				}
			}

			Widgets.Header {
				width: parent.width

				text: "Playback"
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: fadeout_time
					anchors.right: parent.right

					//SpinBox only supports integers, so do everything times 10 to allow 0.1 second intervals.
					value: Math.round(Lyn.Preferences.preferences["player/fadeout"] * 10)
					from: 0
					to: 100
					onValueModified: Lyn.Preferences.set("player/fadeout", value / 10)

					validator: DoubleValidator {
						bottom: fadeout_time.from
						top: fadeout_time.to
					}

					//Convert back and from fixed-point decimals for SpinBox's integer value.
					textFromValue: function(value, locale) {
						return (value / 10.0).toFixed(1);
					}
					valueFromText: function(text, locale) {
						return parseFloat(text) * 10;
					}
				}
				Text {
					anchors.verticalCenter: fadeout_time.verticalCenter

					text: "Fade-out when stopping"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: silence_time
					anchors.right: parent.right

					//SpinBox only supports integers, so do everything times 10 to allow 0.1 second intervals.
					value: Math.round(Lyn.Preferences.preferences["player/silence"] * 10)
					from: 0
					to: 100

					onValueModified: {
						Lyn.Preferences.set("player/silence", value / 10)
					}

					validator: DoubleValidator {
						bottom: fadeout_time.from
						top: fadeout_time.to
					}

					//Convert back and from fixed-point decimals for SpinBox's integer value.
					textFromValue: function(value, locale) {
						return (value / 10.0).toFixed(1);
					}
					valueFromText: function(text, locale) {
						return parseFloat(text) * 10;
					}
				}
				Text {
					anchors.verticalCenter: silence_time.verticalCenter

					text: "Pause between songs"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
				}
			}
		}
	}
}