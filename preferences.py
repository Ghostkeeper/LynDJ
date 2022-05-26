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
import PyQt6.QtCore  # To allow preferences to be reached from QML.
import typing

class Preferences(PyQt6.QtCore.QObject):
	"""
	Stores application preferences and makes sure they get reloaded.
	"""

	"""
	This class is a singleton. This is the one instance.
	"""
	_instance = None

	@classmethod
	def getInstance(cls, _engine=None, _script=None) -> "Preferences":
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
		self.ensure_exists()

		self.defaults = {}
		self.values = {}
		self.load()

	@PyQt6.QtCore.pyqtSlot(str, "QVariant")
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
		directory = os.path.dirname(filepath)

		if not os.path.exists(directory):
			logging.info(f"Preference directory didn't exist yet. Creating it in: {directory}")
			os.makedirs(directory)
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
			if self.defaults[key] != value:  # Not equal to default.
				changed[key] = value
		with open(filepath, "w") as f:
			json.dump(changed, f)

	@PyQt6.QtCore.pyqtSlot(str, "QVariant")
	def set(self, key, value) -> None:
		"""
		Change the current value of a preference.
		:param key: The preference to set.
		:param value: The new value of the preference. This should be a data type that JSON can store.
		"""
		logging.debug(f"Changing preference {key} to {value}.")
		self.values[key] = value
		self.save()  # Immediately save this to disk.
		self.valuesChanged.emit()

	def storage_location(self) -> str:
		"""
		Get the path to the preferences file on this computer.
		:return: A file path to a JSON file where the preferences are stored.
		"""
		try:
			os_path = os.environ["XDG_CONFIG_HOME"]  # XDG standard storage location.
		except KeyError:
			os_path = os.path.expanduser("~/.config")  # Most Linux machines.

		return os.path.join(os_path, "lyndj", "preferences.json")  # Our own addition to the path.

	"""
	Triggered when any preference value changed.
	"""
	valuesChanged = PyQt6.QtCore.pyqtSignal()

	@PyQt6.QtCore.pyqtProperty("QVariantMap", notify=valuesChanged)
	def preferences(self) -> typing.Dict[str, typing.Union[str, int, float, list, dict]]:
		"""
		Get a dictionary of all the current preferences.
		:return: All current preference values.
		"""
		return self.values