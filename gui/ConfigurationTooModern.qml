//Music player software aimed at Lindy Hop DJs.
//Copyright (C) 2023 Ghostkeeper
//This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
//This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
//You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import QtQuick 2.15
import QtQuick.Controls 2.15

Window {
	id: too_modern_dialogue
	x: 100
	y: 100
	width: 600
	height: 300

	property string this_version: "Unknown"
	property string config_version: "Unknown"

	title: "Configuration too modern"

	Component.onCompleted: {
		showNormal();
	}

	Text {
		id: instructions
		anchors {
			left: parent.left
			leftMargin: 10
			right: parent.right
			rightMargin: 10
			top: parent.top
			topMargin: 10
		}

		text: "A more modern version of LynDJ has been used on this computer before. This older version may not be able to understand your preferences and data properly any more. Would you like to try to continue?\n<ul><li>If you continue, your preferences might get corrupt.</li><li>If you reset, the program will restore factory defaults and then start.</li><li>If you cancel, you will be redirected to a website where you can download the most recent version.</li></ul>"
		wrapMode: Text.Wrap
		textFormat: Text.RichText
	}
	Text {
		id: versions
		anchors {
			left: instructions.left
			right: instructions.right
			top: instructions.bottom
			topMargin: 10
		}

		text: "This version: " + too_modern_dialogue.this_version + "\nConfiguration version: " + config_version
		wrapMode: Text.Wrap
	}

	Button {
		id: continue_button
		width: (parent.width - 40) / 3
		anchors {
			left: instructions.left
			top: versions.bottom
			topMargin: 10
		}

		text: "Continue"
	}
	Button {
		width: (parent.width - 40) / 3
		anchors {
			left: continue_button.right
			leftMargin: 10
			top: continue_button.top
		}

		text: "Reset"
	}
	Button {
		width: (parent.width - 40) / 3
		anchors {
			right: instructions.right
			top: continue_button.top
		}

		text: "Cancel"
	}
}