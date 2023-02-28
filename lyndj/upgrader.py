# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import json  # To parse the preferences file.
import logging
import os.path  # To find the configuration files.
import sqlite3  # To parse the metadata database.
import sys  # To quit if the configuration is too modern.
import typing

import lyndj.storage  # To find the configuration files.

class Upgrader:
	"""
	This class checks files in the configuration directories of the application to see if they need to be upgraded to be
	used in the current version of the application.

	If the files are too modern, the current solution is to simply log this, and abort the application.
	"""

	def upgrade(self) -> None:
		"""
		Starting point for the upgrading of the application's configuration directories.
		"""
		# For logging which parts of the configuration are deemed to modern to use.
		# Each entry is a tuple of the type of configuration and its version number.
		too_modern = []  # type: typing.List[typing.Tuple[str, int]]

		# Since the configuration files have never changed yet in the history of this application, we only need to check for files that are too modern for us to understand.
		# If those files are present, we may not parse them properly and may run into errors.
		# So we simply abort the application then.
		metadata_path = os.path.join(lyndj.storage.data(), "metadata.db")
		if os.path.exists(metadata_path):
			connection = sqlite3.connect(metadata_path)
			version_nr = connection.execute("PRAGMA user_version").fetchone()[0]
			if version_nr > 0:
				too_modern.append(("metadata", version_nr))
				logging.error(f"The metadata database is too modern for this version of the application! Version {version_nr}.")
		# lyndj.log is not checked.

		preferences_path = os.path.join(lyndj.storage.config(), "preferences.json")
		if os.path.exists(preferences_path):
			with open(preferences_path) as f:
				try:
					prefs = json.load(f)
					version_nr = prefs["version"]
					if version_nr > 0:
						too_modern.append(("preferences", version_nr))
						logging.error(f"The preferences file is too modern for this version of the application! Version {version_nr}.")
				except json.JSONDecodeError:
					too_modern.append(("preferences", -1))  # Unknown version, was corrupt? Or unintelligible.
					logging.error("The preferences file is not intelligible to this version of the application! Couldn't find the version number.")

		fourier_path = os.path.join(lyndj.storage.cache(), "fourier", "version.txt")
		if os.path.exists(fourier_path):
			with open(fourier_path) as f:
				try:
					version_nr = int(f.read())
					if version_nr > 0:
						too_modern.append(("fourier", version_nr))
						logging.error(f"The Fourier images are too modern for this version of the application! Version {version_nr}.")
				except ValueError:
					too_modern.append(("fourier", -1))  # Unknown version, was corrupt? Or unintelligible.
					logging.error("The Fourier images version file is not intelligible to this version of the application! Couldn't find the version number.")

		if too_modern:
			self.report_too_modern(too_modern)

	def report_too_modern(self, modern_parts: typing.List[typing.Tuple[str, int]]) -> None:
		"""
		Report to the user that parts of the configuration are too modern.
		:param modern_parts: What parts of the configuration are too modern. Could be used to show more information to
		the user.
		"""
		sys.exit()  # For now, simply give up.