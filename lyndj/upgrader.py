# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import json  # To parse the preferences file.
import logging
import os.path  # To find the version number.
import PySide6.QtQml  # To create a dialogue when the configuration is too modern.

import lyndj.storage  # To find the version number.

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
		:param version_nr: The version number found. This would be a newer version than this application.
		"""
		self.application.engine = PySide6.QtQml.QQmlApplicationEngine()
		self.application.engine.load("gui/ConfigurationTooModern.qml")