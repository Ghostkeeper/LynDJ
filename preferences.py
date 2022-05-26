# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import copy
import json  # Preferences are stored in JSON format, which interfaces nicely with Python.
import os  # To know where to store the preferences file.
import os.path  # To construct the path to the preferences file.
import PyQt6.QtCore  # To allow preferences to be reached from QML.
import typing

class Preferences(PyQt6.QtCore.QObject):
    """
    Stores application preferences and makes sure they get reloaded.
    """

    def __init__(self, parent = None) -> None:
        """
        Creates the preferences object
        :param parent:
        """
        super().__init__(parent)
        self.ensure_exists()

        self.defaults = {}
        self.values = {}
        self.load()

    @PyQt6.QtCore.pyqtSlot(str, PyQt6.QtCore.QObject)
    def add(self, key, default) -> None:
        """
        Add a new preference entry.
        :param key: The identifier for the preference.
        :param default: The default value for the preference. This should be a data type that JSON can store.
        """
        if key in self.defaults:
            raise KeyError(f"A preference with the key {key} already exists.")
        self.defaults[key] = default

    def ensure_exists(self) -> None:
        """
        Ensure that the preference file storage exists.
        """
        filepath = self.storage_location()
        directory = os.path.dirname(filepath)
        os.makedirs(directory)
        if not os.path.exists(filepath):  # No preferences file. First time this got launched.
            with open(filepath, "w") as f:
                f.write("{}")  # No overrides to start with.

    def get(self, key) -> typing.Union[str, int, float, list, dict]:
        """
        Get the current value of a preference.
        :param key: The preference to get the value of.
        :return: The current value of the preference.
        """
        return self.values.get(key, self.defaults[key])  # Get from the values, and if not present there, get from the defaults.

    def load(self) -> None:
        """
        Load up the preferences from disk.
        """
        filepath = self.storage_location()
        with open(filepath) as f:
            self.values = json.load(f)

    @PyQt6.QtCore.pyqtSlot(str, PyQt6.QtCore.QObject)
    def set(self, key, value) -> None:
        """
        Change the current value of a preference.
        :param key: The preference to set.
        :param value: The new value of the preference. This should be a data type that JSON can store.
        """
        self.values[key] = value
        self.valuesChanged.emit()

    def storage_location(self) -> str:
        """
        Get the path to the preferences file on this computer.
        :return: A file path to a JSON file where the preferences are stored.
        """
        return os.path.join(os.environ["XDG_CONFIG_HOME"], "lyndj", "preferences.json")

    """
    Triggered when any preference value changed.
    """
    valuesChanged = PyQt6.QtCore.pyqtSignal()

    @PyQt6.QtCore.pyqtProperty("QVariantMap", notify=valuesChanged)
    def values(self) -> typing.Dict[str, typing.Union[str, int, float, list, dict]]:
        """
        Get a dictionary of all the current preferences.
        :return: All current preference values.
        """
        result = copy.copy(self.defaults)
        result.update(self.values)
        return result