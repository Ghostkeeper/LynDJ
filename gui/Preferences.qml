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
			width: preferences_window.width - Lyn.Theme.size["margin"].width - content.rightPadding

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
					anchors {
						verticalCenter: theme_selector.verticalCenter
						left: parent.left
						right: theme_selector.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Theme"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
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
					anchors {
						verticalCenter: fourier_width.verticalCenter
						left: parent.left
						right: fourier_width.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Fourier time resolution"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: fourier_height
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["player/fourier_channels"]
					from: 16
					to: 1024
					stepSize: 8
					onValueModified: Lyn.Preferences.set("player/fourier_channels", value)
				}
				Text {
					anchors {
						verticalCenter: fourier_height.verticalCenter
						left: parent.left
						right: fourier_height.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Fourier frequency resolution"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: fourier_gamma
					anchors.right: parent.right

					//SpinBox only supports integers, so do everything times 10 to allow 0.1 intervals.
					value: Math.round(Lyn.Preferences.preferences["player/fourier_gamma"] * 10)
					from: 1
					to: 100
					onValueModified: Lyn.Preferences.set("player/fourier_gamma", value / 10)

					validator: DoubleValidator {
						bottom: fourier_gamma.from
						top: fourier_gamma.to
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
					anchors {
						verticalCenter: fourier_gamma.verticalCenter
						left: parent.left
						right: fourier_gamma.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Fourier gamma correction"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Widgets.Button {
				text: "Clear stored Fourier images"
				onClicked: Lyn.Player.clear_fourier()
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: slow_bpm
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["playlist/slow_bpm"]
					from: 1
					to: medium_bpm.value - 1
					onValueModified: Lyn.Preferences.set("playlist/slow_bpm", value)
				}
				Text {
					anchors {
						verticalCenter: slow_bpm.verticalCenter
						left: parent.left
						right: slow_bpm.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Slow BPM"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: medium_bpm
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["playlist/medium_bpm"]
					from: slow_bpm.value + 1
					to: fast_bpm.value - 1
					onValueModified: Lyn.Preferences.set("playlist/medium_bpm", value)
				}
				Text {
					anchors {
						verticalCenter: medium_bpm.verticalCenter
						left: parent.left
						right: medium_bpm.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Medium BPM"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: fast_bpm
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["playlist/fast_bpm"]
					from: medium_bpm.value + 1
					to: 1000
					onValueModified: Lyn.Preferences.set("playlist/fast_bpm", value)
				}
				Text {
					anchors {
						verticalCenter: fast_bpm.verticalCenter
						left: parent.left
						right: fast_bpm.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Fast BPM"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
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
					anchors {
						verticalCenter: fadeout_time.verticalCenter
						left: parent.left
						right: fadeout_time.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Fade-out when stopping"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
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
					anchors {
						verticalCenter: silence_time.verticalCenter
						left: parent.left
						right: silence_time.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Pause between songs"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SpinBox {
					id: audio_buffer_size
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["player/buffer_size"]
					from: 1
					to: 10000
					stepSize: 10
					onValueModified: Lyn.Preferences.set("player/buffer_size", value)
				}
				Text {
					anchors {
						verticalCenter: audio_buffer_size.verticalCenter
						left: parent.left
						right: audio_buffer_size.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Audio buffer size (ms)"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Widgets.Header {
				width: parent.width

				text: "AutoDJ"
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.CheckBox {
					id: autodj_enabled
					anchors.right: parent.right

					checkState: Lyn.Preferences.preferences["autodj/enabled"] ? Qt.Checked : Qt.Unchecked
					onClicked: Lyn.Preferences.set("autodj/enabled", checked)
				}
				Text {
					anchors {
						verticalCenter: autodj_enabled.verticalCenter
						left: parent.left
						right: autodj_enabled.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Age variation"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SliderHorizontal {
					id: autodj_age_variation
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["autodj/age_variation"]
					from: 0
					to: 25
					onMoved: Lyn.Preferences.set("autodj/age_variation", value)
				}
				Text {
					anchors {
						verticalCenter: autodj_age_variation.verticalCenter
						left: parent.left
						right: autodj_age_variation.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Age variation"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SliderHorizontal {
					id: autodj_style_variation
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["autodj/style_variation"]
					from: 0
					to: 25
					onMoved: Lyn.Preferences.set("autodj/style_variation", value)
				}
				Text {
					anchors {
						verticalCenter: autodj_style_variation.verticalCenter
						left: parent.left
						right: autodj_style_variation.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Style variation"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SliderHorizontal {
					id: autodj_energy_variation
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["autodj/energy_variation"]
					from: 0
					to: 25
					onMoved: Lyn.Preferences.set("autodj/energy_variation", value)
				}
				Text {
					anchors {
						verticalCenter: autodj_energy_variation.verticalCenter
						left: parent.left
						right: autodj_energy_variation.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Energy variation"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.TextField {
					id: autodj_bpm_cadence
					anchors.right: parent.right

					text: Lyn.Preferences.preferences["autodj/bpm_cadence"]
					validator: RegularExpressionValidator {
						regularExpression: /[0-9]+(,[0-9]+)*/
					}
					onTextEdited: Lyn.Preferences.set("autodj/bpm_cadence", text)
				}
				Text {
					anchors {
						verticalCenter: autodj_bpm_cadence.verticalCenter
						left: parent.left
						right: autodj_bpm_cadence.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "BPM cadence"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SliderHorizontal {
					id: autodj_bpm_precision
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["autodj/bpm_precision"]
					from: 0
					to: 0.5
					onMoved: Lyn.Preferences.set("autodj/bpm_precision", value)
				}
				Text {
					anchors {
						verticalCenter: autodj_bpm_precision.verticalCenter
						left: parent.left
						right: autodj_bpm_precision.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "BPM cadence precision"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SliderHorizontal {
					id: autodj_energy_slider_power
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["autodj/energy_slider_power"]
					from: 0
					to: 2
					onMoved: Lyn.Preferences.set("autodj/energy_slider_power", value)
				}
				Text {
					anchors {
						verticalCenter: autodj_energy_slider_power.verticalCenter
						left: parent.left
						right: autodj_energy_slider_power.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Energy slider power"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}

			Item {
				width: parent.width
				height: childrenRect.height

				Widgets.SliderHorizontal {
					id: autodj_last_played_influence
					anchors.right: parent.right

					value: Lyn.Preferences.preferences["autodj/last_played_influence"]
					from: 0
					to: 2
					onMoved: Lyn.Preferences.set("autodj/last_played_influence", value)
				}
				Text {
					anchors {
						verticalCenter: autodj_last_played_influence.verticalCenter
						left: parent.left
						right: autodj_last_played_influence.left
						rightMargin: Lyn.Theme.size["margin"].width
					}

					text: "Prefer rarely played tracks"
					font: Lyn.Theme.font["default"]
					color: Lyn.Theme.colour["foreground"]
					elide: Text.ElideRight
				}
			}
		}
	}
}