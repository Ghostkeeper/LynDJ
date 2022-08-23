# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import copy
import json  # Preferences are stored in JSON format, which interfaces nicely with Python.
import logging
import os  # To know where to store the preferences file.
import os.path  # To construct the path to the preferences file.
import PySide6.QtCore  # To allow preferences to be reached from QML.
import PySide6.QtQml  # To register the type as singleton in QML.
import typing

import storage  # To know where to store the preferences file.

QML_IMPORT_NAME = "Lyn"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@PySide6.QtQml.QmlElement
@PySide6.QtQml.QmlSingleton
class Preferences(PySide6.QtCore.QObject):
	"""
	Stores application preferences and makes sure they get reloaded.
	"""

	"""
	This class is a singleton. This is the one instance.
	"""
	_instance = None

	@classmethod
	def getInstance(cls, _engine=None, _script=None, _bla=None) -> "Preferences":
		"""
		Gets an instance of the preferences class.

		This ensures that only one instance of the preferences class exists, thus ensuring that all users of the
		preferences talk with the same instance. This allows communicating between these users, whether they be in
		Python or in QML.
		:return: The preferences object.
		"""
		if cls._instance is None:
			logging.debug("Creating preferences instance.")
			cls._instance = Preferences()
		return cls._instance

	def __init__(self) -> None:
		"""
		Creates the preferences object
		:param parent:
		"""
		super().__init__(None)

		self.save_timer = PySide6.QtCore.QTimer()
		self.save_timer.setSingleShot(True)
		self.save_timer.setInterval(250)  # After a preference changed, after 250ms, it'll auto-save.
		self.save_timer.timeout.connect(self.save)

		storage.ensure_exists()
		self.ensure_exists()

		self.defaults = {}
		self.values = {}
		self.load()

	@PySide6.QtCore.Slot(str, "QVariant")
	def add(self, key, default) -> None:
		"""
		Add a new preference entry.
		:param key: The identifier for the preference.
		:param default: The default value for the preference. This should be a data type that JSON can store.
		"""
		if key in self.defaults:
			raise KeyError(f"A preference with the key {key} already exists.")
		logging.debug(f"Adding preference {key} with default {default}.")
		self.defaults[key] = default
		if key not in self.values:
			self.values[key] = default

	def ensure_exists(self) -> None:
		"""
		Ensure that the preference file storage exists.
		"""
		filepath = self.storage_location()
		if not os.path.exists(filepath):  # No preferences file. First time this got launched.
			logging.info(f"Preference file didn't exist yet. Creating it in: {filepath}")
			with open(filepath, "w") as f:
				f.write("{}")  # No overrides to start with.

	def get(self, key) -> typing.Union[str, int, float, list, dict]:
		"""
		Get the current value of a preference.
		:param key: The preference to get the value of.
		:return: The current value of the preference.
		"""
		return self.values[key]

	def has(self, key) -> bool:
		"""
		Tests whether a preference with a given key exists.
		:param key: The preference to test for.
		:return: ``True`` if it exists, or ``False`` if it doesn't.
		"""
		return key in self.defaults

	def load(self) -> None:
		"""
		Load up the preferences from disk.
		"""
		filepath = self.storage_location()
		logging.info(f"Loading preferences from: {filepath}")
		with open(filepath) as f:
			self.values = copy.deepcopy(self.defaults)
			self.values.update(json.load(f))

	def save(self) -> None:
		"""
		Store the current state of the preferences to disk.
		"""
		filepath = self.storage_location()
		logging.debug(f"Saving preferences.")

		changed = {}
		for key, value in self.values.items():
			if key not in self.defaults:  # Value is not defined in defaults. Possibly edited preferences file.
				continue
			if self.defaults[key] != value:  # Not equal to default.
				changed[key] = value
		with open(filepath, "w") as f:
			json.dump(changed, f, indent="\t")

	@PySide6.QtCore.Slot(str, "QVariant")
	def set(self, key, value) -> None:
		"""
		Change the current value of a preference.
		:param key: The preference to set.
		:param value: The new value of the preference. This should be a data type that JSON can store.
		"""
		logging.debug(f"Changing preference {key} to {value}.")
		self.values[key] = value
		self.save_timer.start()
		self.valuesChanged.emit()

	def storage_location(self) -> str:
		"""
		Get the path to the preferences file on this computer.
		:return: A file path to a JSON file where the preferences are stored.
		"""
		return os.path.join(storage.config(), "preferences.json")

	"""
	Triggered when any preference value changed.
	"""
	valuesChanged = PySide6.QtCore.Signal()

	@PySide6.QtCore.Property("QVariantMap", notify=valuesChanged)
	def preferences(self) -> typing.Dict[str, typing.Union[str, int, float, list, dict]]:
		"""
		Get a dictionary of all the current preferences.
		:return: All current preference values.
		"""
		return self.values