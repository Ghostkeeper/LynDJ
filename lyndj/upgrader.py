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
import sqlite3  # To upgrade the metadata database.
import sys  # To cancel start-up if requested by the user.
import time  # For a custom event loop for the dialogue to ask what to do when the configuration is too modern.
import typing

import lyndj.application  # To find the application version number.
import lyndj.storage  # To find the configuration to upgrade.

class ConfigurationTooModernDialogue(PySide6.QtWidgets.QSplashScreen):
	"""
	A custom splash screen that shows the user that their configuration files are too modern, providing them with a
	choice on how to proceed.

	This uses the ``QSplashScreen`` class since it's the only class that can be shown before the main window is created,
	without interfering with the way resources are used in the main window.
	"""

	def __init__(self, config_version: str) -> None:
		"""
		Creates the dialogue object in memory, and shows it to the user.
		:param config_version: The version of the application that wrote the current configuration files.
		"""
		super().__init__()
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
		painter.drawText(10, 10 + 3*18 + 10 + 4*18 + 10, self.width() - 20, 18, text_flags, "This version: " + lyndj.application.Application.version)
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
		:param application: The application this is running in, for maintaining any dialogues.
		"""
		self.application = application

	def upgrade(self):
		"""
		Starting point for the upgrading of the application's configuration directories.
		"""
		application_version = self.parse_version(lyndj.application.Application.version)
		version_str = self.get_version()
		version_nr = (0, 0, 0)
		try:
			version_nr = self.parse_version(version_str)
		except ValueError:
			version_str = "unknown"
		if version_str == "unknown":
			logging.error("The preferences file is not intelligible to this version of the application! Couldn't find the version number.")
			self.report_too_modern(version_str)
			return

		if version_nr > application_version:
			logging.error(f"The preferences file is too modern for this version of the application! Version {version_str}.")
			self.report_too_modern(version_str)
			return

		# Map upgrades to finally arrive at the current version.
		upgrade_table = {
			"1.0.0": self.upgrade_1_0_0_to_1_1_0
		}

		while version_str in upgrade_table:
			upgrade_table[version_str]()  # Execute that upgrade.
			version_str = self.get_version()

	def get_version(self) -> str:
		"""
		Get the current version number of the configuration.
		:return: A version number, as a string, or "unknown" if it couldn't be found.
		"""
		preferences_path = os.path.join(lyndj.storage.config(), "preferences.json")
		if not os.path.exists(preferences_path):
			return lyndj.application.Application.version  # Since we don't have any config yet, nothing to upgrade. Pretend it's the current version.
		with open(preferences_path) as f:
			try:
				prefs = json.load(f)
				return prefs["version"]
			except (json.JSONDecodeError, KeyError):
				return "unknown"

	@classmethod
	def parse_version(cls, version: str) -> typing.Tuple[int, int, int]:
		"""
		Parse a version number into a tuple which can be compared lexicographically.
		:param version: The version number as a string.
		:return: A tuple representing that version number, which can be compared lexicographically.
		"""
		return typing.cast(typing.Tuple[int, int, int], tuple(int(component) for component in version.split(".")))

	def report_too_modern(self, version_nr: str) -> None:
		"""
		Report to the user that parts of the configuration are too modern.

		This shows the user a dialogue with a choice of what to do in this case.
		:param version_nr: The version number found. This would be a newer version than this application.
		"""
		dialogue = ConfigurationTooModernDialogue(version_nr)
		# While the dialogue is shown, make a miniature event loop to allow the user to click on the buttons.
		self.application.processEvents()
		while dialogue.isVisible():
			time.sleep(0.1)
			self.application.processEvents()

	def upgrade_1_0_0_to_1_1_0(self) -> None:
		"""
		Upgrades the configuration from version 1.0.0 to version 1.1.0.
		"""
		logging.info("Upgrading configuration from 1.0.0 to 1.1.0.")
		# Upgrade preferences file:
		# * Update version number.
		preferences_path = os.path.join(lyndj.storage.config(), "preferences.json")
		with open(preferences_path) as f:
			try:
				prefs = json.load(f)
				prefs["version"] = "1.1.0"  # Upgrade the version number.
				with open(preferences_path, "w") as f:
					json.dump(prefs, f, indent="\t")
				logging.debug("Upgraded preferences file to 1.1.0.")
			except json.JSONDecodeError:
				logging.error("Failed to load preferences file while upgrading. Configuration might get corrupt!")  # But do continue trying to upgrade the rest to minimise damage.

		# Update metadata database:
		# * Add cut_start and cut_end timestamps.
		metadata_path = os.path.join(lyndj.storage.data(), "metadata.db")
		connection = sqlite3.connect(metadata_path)
		connection.execute("ALTER TABLE metadata ADD cut_start real")
		connection.execute("ALTER TABLE metadata ADD cut_end real")
		connection.commit()
		logging.debug("Upgraded metadata database to 1.1.0.")