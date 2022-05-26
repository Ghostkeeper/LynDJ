# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import json  # Theme files are JSON formatted.
import logging
import os.path  # To find the theme file.
import PyQt6.QtCore  # To allow QML to get the theme data, and to export sizes.
import PyQt6.QtGui  # To export colours.

import preferences  # To get which theme to load.

class Theme(PyQt6.QtCore.QObject):
    """
    Represents a theme, which contains a list of sizes and colours that are consistent throughout the application.
    """

    """
    This class is a singleton. This is the singleton instance.
    """
    _instance = None

    @classmethod
    def getInstance(cls, _engine=None, _script=None) -> "Theme":
        """
        Gets an instance of the theme class.

        This ensures that only one instance of the theme class exists, thus ensuring that all users of the theme talk
        with the same instance. This allows the theme to change in run-time and all QML to update with it.
        :return: The theme object.
        """
        if cls._instance is None:
            logging.debug("Creating theme instance.")
            cls._instance = Theme()
        return cls._instance

    def __init__(self):
        super().__init__(None)

        preferences.Preferences.getInstance().add("theme", "light")

        self.sizes = {}
        self.colours = {}

        self.load()

    def load(self):
        logging.info("Loading theme.")
        theme_name = preferences.Preferences.getInstance().get("theme")
        theme_file = os.path.join("theme", theme_name + ".json")
        with open(theme_file) as f:
            theme_dict = json.load(f)
            for key, dimensions in theme_dict["sizes"].items():
                self.sizes[key] = PyQt6.QtCore.QSizeF(dimensions[0], dimensions[1])
            for key, channels in theme_dict["colours"].items():
                self.colours[key] = PyQt6.QtGui.QColor(channels[0], channels[1], channels[2], channels[3])  # RGBA.