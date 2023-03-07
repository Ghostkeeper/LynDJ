# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import json  # To parse the preferences file.
import logging
import os.path  # To find the files to upgrade.
import PySide6.QtCore  # To create a dialogue to ask what to do when the configuration is too modern.
import PySide6.QtGui  # To create a dialogue to ask what to do when the configuration is too modern.
import PySide6.QtWidgets  # To create a dialogue to ask what to do when the configuration is too modern.
import sys  # To cancel start-up if requested by the user.
import time  # For a custom event loop for the dialogue to ask what to do when the configuration is too modern.
import typing

import lyndj.storage  # To find the configuration to upgrade.

if typing.TYPE_CHECKING:
	import lyndj.application

class ConfigurationTooModernDialogue(PySide6.QtWidgets.QSplashScreen):
	"""
	A custom splash screen that shows the user that their configuration files are too modern, providing them with a
	choice on how to proceed.

	This uses the ``QSplashScreen`` class since it's the only class that can be shown before the main window is created,
	without interfering with the way resources are used in the main window.
	"""

	def __init__(self, application_version: str, config_version: str) -> None:
		"""
		Creates the dialogue object in memory, and shows it to the user.
		:param application_version: The current version of the application.
		:param config_version: The version of the application that wrote the current configuration files.
		"""
		super().__init__()
		self.application_version = application_version
		self.config_version = config_version

		self.setGeometry(100, 100, 600, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10 + 40 + 10)
		self.show()

	def drawContents(self, painter: PySide6.QtGui.QPainter) -> None:
		"""
		Draw the contents of the dialogue.

		This draws all of the contents at once, regardless of what parts of it need to be redrawn. It's not particularly
		efficient in that regard.
		:param painter: The painter with which to paint the contents.
		"""
		painter.save()

		text_flags = PySide6.QtCore.Qt.AlignmentFlag.AlignLeft | PySide6.QtCore.Qt.AlignmentFlag.AlignTop | PySide6.QtCore.Qt.TextFlag.TextWordWrap
		circle_path = PySide6.QtGui.QPainterPath()
		circle_path.addEllipse(-3, -3, 6, 6)
		black_brush = PySide6.QtGui.QBrush(PySide6.QtGui.QColor(0, 0, 0))

		# Instructive text.
		painter.drawText(10, 10, self.width() - 20, 3 * 18, text_flags, "A more modern version of LynDJ has been used on this computer before. This older version may not be able to understand your preferences and data properly any more. Would you like to try to continue?")
		# Three options.
		painter.fillPath(circle_path.translated(20, 10 + 3*18 + 10 + 9), black_brush)
		painter.drawText(30, 10 + 3*18 + 10, self.width() - 40, 18, text_flags, "If you continue, your preferences might get corrupt.")
		painter.fillPath(circle_path.translated(20, 10 + 3*18 + 10 + 18 + 9), black_brush)
		painter.drawText(30, 10 + 3*18 + 10 + 18, self.width() - 40, 18, text_flags, "If you reset, the program will restore factory defaults and then start.")
		painter.fillPath(circle_path.translated(20, 10 + 3*18 + 10 + 2*18 + 9), black_brush)
		painter.drawText(30, 10 + 3*18 + 10 + 2*18, self.width() - 40, 2 * 18, text_flags, "If you cancel, you will be redirected to a website where you can download the most recent version.")
		# Version numbers.
		painter.drawText(10, 10 + 3*18 + 10 + 4*18 + 10, self.width() - 20, 18, text_flags, "This version: " + self.application_version)
		painter.drawText(10, 10 + 3*18 + 10 + 4*18 + 10 + 18, self.width() - 20, 18, text_flags, "Configuration version: " + self.config_version)
		# Buttons.
		button_width = int((self.width() - 40) / 3)
		button_text_flags = PySide6.QtCore.Qt.AlignmentFlag.AlignCenter
		painter.drawRect(10, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10, button_width, 30)
		painter.drawText(10, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10, button_width, 30, button_text_flags, "Continue")
		painter.drawRect(10 + button_width + 10, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10, button_width, 30)
		painter.drawText(10 + button_width + 10, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10, button_width, 30, button_text_flags, "Reset")
		painter.drawRect(10 + button_width * 2 + 20, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10, button_width, 30)
		painter.drawText(10 + button_width * 2 + 20, 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10, button_width, 30, button_text_flags, "Cancel")

		painter.restore()
		super().drawContents(painter)

	def mousePressEvent(self, _: PySide6.QtGui.QMouseEvent) -> None:
		"""
		Catch mouse press events so that the screen doesn't pass them on to any window below it in the operating system.
		:param _: A mouse event, which this screen ignores.
		"""
		pass  # Do nothing.

	def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
		"""
		Processes any clicks on the window.
		:param event: The mouse event that occurred.
		"""
		x = event.pos().x()
		y = event.pos().y()
		button_width = int((self.width() - 40) / 3)

		if y < 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10:  # Above the buttons.
			return
		elif y >= 10 + 3*18 + 10 + 4*18 + 10 + 2*18 + 10 + 30:  # Below the buttons.
			return
		elif 10 <= x < 10 + button_width:  # Continue button is clicked.
			self.hide()
		elif 10 + button_width + 10 <= x < 10 + button_width * 2:  # Reset button is clicked.
			lyndj.storage.reset_to_factory_defaults()
			self.hide()
		elif 10 + button_width * 2 + 20 <= x < 10 + button_width * 3 + 20:  # Cancel button is clicked.
			PySide6.QtGui.QDesktopServices.openUrl("https://github.com/Ghostkeeper/LynDJ/releases/latest")
			sys.exit()

class Upgrader:
	"""
	This class checks files in the configuration directories of the application to see if they need to be upgraded to be
	used in the current version of the application.

	If the files are too modern, the current solution is to simply log this, and abort the application.
	"""

	def __init__(self, application):
		"""
		Creates the upgrader instance.
		:param application: The application instance to link to when creating any QML dialogues.
		"""
		self.application = application

	def upgrade(self) -> bool:
		"""
		Starting point for the upgrading of the application's configuration directories.
		:return: Whether the upgrade process was successful.
		"""
		# Since the configuration files have never changed yet in the history of this application, we just need to check if the configuration is more modern than what this version understands.
		# If it is present and too modern, we may not parse it properly and run into errors.
		preferences_path = os.path.join(lyndj.storage.config(), "preferences.json")
		if os.path.exists(preferences_path):
			with open(preferences_path) as f:
				try:
					prefs = json.load(f)
					version_nr = prefs["version"]
					if version_nr != self.application.applicationVersion():
						logging.error(f"The preferences file is too modern for this version of the application! Version {version_nr}.")
						self.report_too_modern(version_nr)
						return False
				except json.JSONDecodeError:
					logging.error("The preferences file is not intelligible to this version of the application! Couldn't find the version number.")
					self.report_too_modern("unknown")
					return False
		return True

	def report_too_modern(self, version_nr: str) -> None:
		"""
		Report to the user that parts of the configuration are too modern.

		This shows the user a dialogue with a choice of what to do in this case.
		:param version_nr: The version number found. This would be a newer version than this application.
		"""
		dialogue = ConfigurationTooModernDialogue(self.application.applicationVersion(), version_nr)
		# While the dialogue is shown, make a miniature event loop to allow the user to click on the buttons.
		self.application.processEvents()
		while dialogue.isVisible():
			time.sleep(0.1)
			self.application.processEvents()