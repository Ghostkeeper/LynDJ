# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os
import PyQt6.QtCore
import PyQt6.QtGui  # This is a GUI application.
import PyQt6.QtQml  # To register types with the QML engine.

import music_directory
import preferences
import storage
import theme

class Application(PyQt6.QtGui.QGuiApplication):
	"""
	The Qt application that runs the whole thing.

	This provides a QML engine and keeps it running until the application quits.
	"""

	def __init__(self, argv):
		"""
		Starts the application.
		:param argv: Command-line parameters provided to the application. Qt understands some of these.
		"""
		logging.info("Starting application.")
		super().__init__(argv)

		# TODO: Move creation of browse path preference to path browser class.
		prefs = preferences.Preferences.getInstance()
		music_locations = PyQt6.QtCore.QStandardPaths.standardLocations(PyQt6.QtCore.QStandardPaths.StandardLocation.MusicLocation)
		if music_locations:
			browse_path = music_locations[0]
		else:
			browse_path = os.path.expanduser("~/")
		prefs.add("browse_path", browse_path)

		logging.debug("Registering QML types.")
		PyQt6.QtQml.qmlRegisterSingletonType(preferences.Preferences, "Lyn", 1, 0, preferences.Preferences.getInstance, "Preferences")
		PyQt6.QtQml.qmlRegisterSingletonType(theme.Theme, "Lyn", 1, 0, theme.Theme.getInstance, "Theme")
		PyQt6.QtQml.qmlRegisterType(music_directory.MusicDirectory, "Lyn", 1, 0, "MusicDirectory")

		logging.debug("Loading QML engine.")
		self.engine = PyQt6.QtQml.QQmlApplicationEngine()
		self.engine.quit.connect(self.quit)
		self.engine.load("gui/MainWindow.qml")

		logging.info("Start-up complete.")