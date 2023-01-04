# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os  # To find the home directory, resource files and to edit environment variables in the local context.
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "YES"  # Before importing pygame!
import pygame  # To initialise the sound engine.
import PySide6.QtCore
import PySide6.QtGui  # This is a GUI application.
import PySide6.QtQml  # To register types with the QML engine.

import background_tasks  # To register this with QML.
import metadata  # Loading metadata on start-up.
import music_directory  # To register this with QML.
import player  # To register this with QML.
import playlist  # To register this with QML.
import preferences  # To register this with QML and define some preferences.
import storage  # To find the window icon.
import theme  # To register this with QML.
import waypoints_timeline  # To register this with QML.

class Application(PySide6.QtGui.QGuiApplication):
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
		music_locations = PySide6.QtCore.QStandardPaths.standardLocations(PySide6.QtCore.QStandardPaths.StandardLocation.MusicLocation)
		if music_locations:
			browse_path = music_locations[0]
		else:
			browse_path = os.path.expanduser("~/")
		prefs.add("browse_path", browse_path)

		logging.debug("Loading metadata database.")
		metadata.load()

		logging.debug("Loading media engine.")
		pygame.init()

		logging.debug("Registering QML types.")
		self.create_gui_preferences()
		PySide6.QtQml.qmlRegisterSingletonInstance(preferences.Preferences, "Lyn", 1, 0, "Preferences", preferences.Preferences.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(theme.Theme, "Lyn", 1, 0, "Theme", theme.Theme.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(playlist.Playlist, "Lyn", 1, 0, "Playlist", playlist.Playlist.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(Application, "Lyn", 1, 0, "Application", self)
		PySide6.QtQml.qmlRegisterSingletonInstance(player.Player, "Lyn", 1, 0, "Player", player.Player.get_instance())
		PySide6.QtQml.qmlRegisterSingletonInstance(background_tasks.BackgroundTasks, "Lyn", 1, 0, "BackgroundTasks", background_tasks.BackgroundTasks.get_instance())
		PySide6.QtQml.qmlRegisterType(music_directory.MusicDirectory, "Lyn", 1, 0, "MusicDirectory")
		PySide6.QtQml.qmlRegisterType(waypoints_timeline.WaypointsTimeline, "Lyn", 1, 0, "WaypointsTimeline")

		logging.debug("Loading QML engine.")
		self.engine = PySide6.QtQml.QQmlApplicationEngine()
		self.engine.quit.connect(self.quit)
		self.engine.load("gui/MainWindow.qml")

		# Icon needs to be added AFTER the main window is loaded.
		self.setWindowIcon(PySide6.QtGui.QIcon(os.path.join(storage.source(), "icon.svg")))

		logging.info("Start-up complete.")

	def create_gui_preferences(self):
		"""
		Creates preferences that are used in the GUI.

		The QML can't create new preferences. While the scope of the GUI would claim these preferences for themselves,
		it can't be defined there. We should define them here instead.
		"""
		prefs = preferences.Preferences.getInstance()
		prefs.add("window/width", 1280)
		prefs.add("window/height", 720)
		prefs.add("window/x", 100)
		prefs.add("window/y", 100)
		prefs.add("window/visibility", "normal")
		prefs.add("divider_pos", 0.5)  # As a fraction of the width of the window.

	@PySide6.QtCore.Slot()
	def closing(self) -> None:
		"""
		Triggered when the main window is closed.
		"""
		player.Player.control_thread = None