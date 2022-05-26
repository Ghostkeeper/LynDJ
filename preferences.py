# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import json  # Preferences are stored in JSON format, which interfaces nicely with Python.
import os  # To know where to store the preferences file.
import os.path  # To construct the path to the preferences file.
import PyQt6.QtCore  # To allow preferences to be reached from QML.

class Preferences(PyQt6.QtCore.QObject):
    """
    Stores application preferences and makes sure they get reloaded.
    """

    def __init__(self, parent = None):
        """
        Creates the preferences object
        :param parent:
        """
        super().__init__(parent)
        self.ensure_exists()

        self.defaults = {}
        self.values = {}
        self.load()

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

    def load(self):
        filepath = self.storage_location()
        with open(filepath) as f:
            self.values = json.load(f)

    def storage_location(self):
        return os.path.join(os.environ["XDG_CONFIG_HOME"], "lyndj", "preferences.json")