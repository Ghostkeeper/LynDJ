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
import typing

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

		self.load(update_gui=False)

	"""
	Triggered when the theme changes.
	"""
	themeChanged = PyQt6.QtCore.pyqtSignal()

	@PyQt6.QtCore.pyqtProperty("QVariantMap", notify=themeChanged)
	def colour(self) -> typing.Dict[str, PyQt6.QtGui.QColor]:
		"""
		Get the dictionary of colours.
		:return: A dictionary of all colours.
		"""
		return self.colours

	def load(self, update_gui=True) -> None:
		"""
		Load the theme from the theme file.

		The currently set theme from the preferences will be used for this.
		:param trigger_change: Whether to notify the GUI that the theme changed. This should not be done for the initial
		load of the theme, to prevent essentially loading the GUI twice.
		"""
		theme_name = preferences.Preferences.getInstance().get("theme")
		theme_file = os.path.join("theme", theme_name + ".json")
		logging.info(f"Loading theme from: {theme_file}")
		with open(theme_file) as f:
			theme_dict = json.load(f)
			for key, dimensions in theme_dict["sizes"].items():
				while type(dimensions) == str:  # Refers to a different theme entry.
					dimensions = theme_dict["sizes"][dimensions]
				self.sizes[key] = PyQt6.QtCore.QSizeF(dimensions[0], dimensions[1])
			for key, channels in theme_dict["colours"].items():
				while type(channels) == str:  # Refers to a different theme entry.
					channels = theme_dict["colours"][channels]
				self.colours[key] = PyQt6.QtGui.QColor(channels[0], channels[1], channels[2], channels[3])  # RGBA.
			if update_gui:
				self.themeChanged.emit()

	@PyQt6.QtCore.pyqtProperty("QVariantMap", notify=themeChanged)
	def size(self) -> typing.Dict[str, PyQt6.QtCore.QSizeF]:
		"""
		Get the dictionary of sizes.
		:return: A dictionary of all theme sizes.
		"""
		return self.sizes