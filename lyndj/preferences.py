# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import copy  # Copying values from defaults to the actual values, so that defaults don't get changed by reference.
import json  # Preferences are stored in JSON format, which interfaces nicely with Python.
import logging
import os  # To know where to store the preferences file.
import os.path  # To construct the path to the preferences file.
import PySide6.QtCore  # To allow preferences to be reached from QML.
import PySide6.QtQml  # To register the type as singleton in QML.
import typing

import lyndj.application  # To get the current application version.
import lyndj.storage  # To know where to store the preferences file.

QML_IMPORT_NAME = "Lyn"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@PySide6.QtQml.QmlElement
@PySide6.QtQml.QmlSingleton
class Preferences(PySide6.QtCore.QObject):
	"""
	Stores application preferences and makes sure they get reloaded.
	"""

	_instance: typing.Optional["Preferences"] = None
	"""
	This class is a singleton. This is the one instance.
	"""

	@classmethod
	def get_instance(cls, _engine: typing.Optional[PySide6.QtQml.QQmlApplicationEngine]=None, _script: typing.Optional[PySide6.QtQml.QQmlFile]=None) -> "Preferences":
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
		Creates the preferences object.
		:param parent: If this instance is part of a QML scene, the parent QML element.
		"""
		super().__init__(None)

		self.save_timer = PySide6.QtCore.QTimer()
		self.save_timer.setSingleShot(True)
		self.save_timer.setInterval(250)  # After a preference changed, after 250ms, it'll auto-save.
		self.save_timer.timeout.connect(self.save)

		self.ensure_exists()

		self.defaults = {}
		self.values = {}
		self.load()

	@PySide6.QtCore.Slot(str, "QVariant")
	def add(self, key: str, default: typing.Any) -> None:
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
			self.values[key] = copy.copy(default)  # Make a copy, so that the default doesn't accidentally change if modified by reference.

	def ensure_exists(self) -> None:
		"""
		Ensure that the preference file storage exists.
		"""
		filepath = self.storage_location()
		if not os.path.exists(filepath):  # No preferences file. First time this got launched.
			logging.info(f"Preference file didn't exist yet. Creating it in: {filepath}")
			with open(filepath, "w") as f:
				f.write("{}")  # No overrides to start with.

	def get(self, key: str) -> typing.Union[str, int, float, list, dict]:
		"""
		Get the current value of a preference.
		:param key: The preference to get the value of.
		:return: The current value of the preference.
		"""
		return self.values[key]  # Get by reference! Otherwise you can't change lists and dicts stored in the preferences.

	def has(self, key: str) -> bool:
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
			try:
				self.values.update(json.load(f))
			except json.JSONDecodeError:
				logging.error("Could not load preferences. Resetting preferences!")

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
		changed["version"] = lyndj.application.Application.version
		with open(filepath, "w") as f:
			json.dump(changed, f, indent="\t")

	@PySide6.QtCore.Slot(str, "QVariant")
	def set(self, key: str, value: typing.Any) -> None:
		"""
		Change the current value of a preference.
		:param key: The preference to set.
		:param value: The new value of the preference. This should be a data type that JSON can store.
		"""
		logging.debug(f"Changing preference {key} to {value}.")
		self.values[key] = value
		self.save_timer.start()
		self.valuesChanged.emit(key)

	@PySide6.QtCore.Slot(str, int, "QVariant")
	def set_element(self, key: str, index: typing.Union[int, str], value: typing.Any) -> None:
		"""
		Change an element in a list-type or dict-type preference.
		:param key: The preference to change an element of.
		:param index: The index in the list, or the key in the dict to change.
		:param value: The new value for the element in the list or dict.
		"""
		logging.debug(f"Changing preference {key}, index {index} to {value}.")
		self.values[key][index] = value
		self.changed_internally(key)

	def changed_internally(self, key: typing.Union[int, str]) -> None:
		"""
		Trigger an update of things listening to the preferences, after something changed internally in an object saved
		in the preferences.

		This should be used, for instance, if an element of a dict has changed, or if appending or removing from a list.
		:param key: The element that changed. This is not used for now.
		"""
		logging.debug(f"Changing preference {key} internally.")
		self.save_timer.start()
		self.valuesChanged.emit(key)

	def storage_location(self) -> str:
		"""
		Get the path to the preferences file on this computer.
		:return: A file path to a JSON file where the preferences are stored.
		"""
		return os.path.join(lyndj.storage.config(), "preferences.json")

	valuesChanged = PySide6.QtCore.Signal(str)
	"""
	Triggered when any preference value changed.
	"""

	@PySide6.QtCore.Property("QVariantMap", notify=valuesChanged)
	def preferences(self) -> typing.Dict[str, typing.Any]:
		"""
		Get a dictionary of all the current preferences.
		:return: All current preference values.
		"""
		return self.values