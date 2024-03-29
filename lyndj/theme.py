# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import json  # Theme files are JSON formatted.
import logging
import os.path  # To find the theme file.
import PySide6.QtCore  # To allow QML to get the theme data, and to export sizes.
import PySide6.QtGui  # To export colours.
import typing

import lyndj.preferences  # To get which theme to load.
import lyndj.storage  # To find the theme directory.

class Theme(PySide6.QtCore.QObject):
	"""
	Represents a theme, which contains a list of sizes and colours that are consistent throughout the application.
	"""

	"""
	This class is a singleton. This is the singleton instance.
	"""
	_instance: typing.Optional["Theme"] = None

	@classmethod
	def get_instance(cls, _engine=None, _script=None) -> "Theme":
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

	def __init__(self) -> None:
		"""
		Construct a new instance of the Theme class.
		"""
		super().__init__(None)

		prefs = lyndj.preferences.Preferences.get_instance()
		prefs.add("theme", "LightDeco")
		prefs.valuesChanged.connect(self.change_theme)

		self.sizes = {}
		self.colours = {}
		self.fonts = {}
		self.icons = {}

		self.load(update_gui=False)

	def change_theme(self, preference_key: str) -> None:
		"""
		Triggered when the preferences change, this function changes the theme if necessary.
		:param preference_key: The preference that was changed.
		"""
		if preference_key == "theme":
			self.load()

	themeChanged = PySide6.QtCore.Signal()
	"""
	Triggered when the theme changes.
	"""

	@PySide6.QtCore.Property("QVariantMap", notify=themeChanged)
	def colour(self) -> typing.Dict[str, PySide6.QtGui.QColor]:
		"""
		Get the dictionary of colours.
		:return: A dictionary of all colours.
		"""
		return self.colours

	@PySide6.QtCore.Property("QVariantMap", notify=themeChanged)
	def font(self) -> typing.Dict[str, PySide6.QtGui.QFont]:
		"""
		Get the dictionary of fonts.
		:return: A dictionary of all fonts.
		"""
		return self.fonts

	@PySide6.QtCore.Property("QVariantMap", notify=themeChanged)
	def icon(self) -> typing.Dict[str, str]:
		"""
		Get the dictionary of icon names to icon paths.
		:return: A dictionary mapping item names to their paths.
		"""
		return self.icons

	def load(self, update_gui: bool=True) -> None:
		"""
		Load the theme from the theme file.

		The currently set theme from the preferences will be used for this.
		:param update_gui: Whether to notify the GUI that the theme changed. This should not be done for the initial
		load of the theme, to prevent essentially loading the GUI twice.
		"""
		theme_name = lyndj.preferences.Preferences.get_instance().get("theme")
		theme_directory = os.path.join(lyndj.storage.source(), "theme", theme_name)
		logging.info(f"Loading theme from: {theme_directory}")

		theme_file = os.path.join(theme_directory, "theme.json")
		with open(theme_file) as f:
			theme_dict = json.load(f)

		for key, dimensions in theme_dict["sizes"].items():
			while type(dimensions) is str:  # Refers to a different theme entry.
				dimensions = theme_dict["sizes"][dimensions]
			self.sizes[key] = PySide6.QtCore.QSizeF(dimensions[0], dimensions[1])
		for key, channels in theme_dict["colours"].items():
			while type(channels) is str:  # Refers to a different theme entry.
				channels = theme_dict["colours"][channels]
			self.colours[key] = PySide6.QtGui.QColor(channels[0], channels[1], channels[2], channels[3])  # RGBA.
		for key, parameters in theme_dict["fonts"].items():
			while type(parameters) is str:
				parameters = theme_dict["fonts"][parameters]
			font = PySide6.QtGui.QFont()
			font.setFamily(parameters["family"])
			font.setPointSize(parameters["size"])
			font.setWeight(PySide6.QtGui.QFont.Weight(parameters["weight"]))
			font.setItalic(parameters.get("italic", False))
			self.fonts[key] = font
		if update_gui:
			self.themeChanged.emit()

		for icon_file in os.listdir(theme_directory):
			icon_name, ext = os.path.splitext(icon_file)
			if ext != ".svg":
				continue  # Only load SVGs as icons.
			icon_path = os.path.join(theme_directory, icon_file)
			icon_url = PySide6.QtCore.QUrl.fromLocalFile(icon_path)
			self.icons[icon_name] = icon_url

	@PySide6.QtCore.Property("QVariantMap", notify=themeChanged)
	def size(self) -> typing.Dict[str, PySide6.QtCore.QSizeF]:
		"""
		Get the dictionary of sizes.
		:return: A dictionary of all theme sizes.
		"""
		return self.sizes

	@PySide6.QtCore.Property("QStringList", constant=True)
	def theme_names(self) -> typing.List[str]:
		"""
		Get the list of the available themes to choose from.
		:return: A list of theme names.
		"""
		return os.listdir(os.path.join(lyndj.storage.source(), "theme"))