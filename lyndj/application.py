# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os  # To find the home directory, resource files and to edit environment variables in the local context.
import PySide6.QtCore
import PySide6.QtGui  # To give the application an icon.
import PySide6.QtQml  # To register types with the QML engine.
import PySide6.QtWidgets  # This is an application.

import lyndj.background_tasks  # To register this with QML.
import lyndj.history  # To register this with QML.
import lyndj.metadata  # Loading metadata on start-up.
import lyndj.music_directory  # To register this with QML.
import lyndj.player  # To register this with QML.
import lyndj.playlist  # To register this with QML.
import lyndj.preferences  # To register this with QML and define some preferences.
import lyndj.storage  # To find the window icon.
import lyndj.theme  # To register this with QML.
import lyndj.waypoints_timeline  # To register this with QML.

class Application(PySide6.QtWidgets.QApplication):
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

		logging.debug("Loading metadata database.")
		lyndj.metadata.load()

		logging.debug("Registering QML types.")
		self.create_gui_preferences()
		PySide6.QtQml.qmlRegisterSingletonInstance(lyndj.preferences.Preferences, "Lyn", 1, 0, "Preferences", lyndj.preferences.Preferences.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(lyndj.theme.Theme, "Lyn", 1, 0, "Theme", lyndj.theme.Theme.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(lyndj.playlist.Playlist, "Lyn", 1, 0, "Playlist", lyndj.playlist.Playlist.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(lyndj.history.History, "Lyn", 1, 0, "History", lyndj.history.History.getInstance())
		PySide6.QtQml.qmlRegisterSingletonInstance(Application, "Lyn", 1, 0, "Application", self)
		PySide6.QtQml.qmlRegisterSingletonInstance(lyndj.player.Player, "Lyn", 1, 0, "Player", lyndj.player.Player.get_instance())
		PySide6.QtQml.qmlRegisterSingletonInstance(lyndj.background_tasks.BackgroundTasks, "Lyn", 1, 0, "BackgroundTasks", lyndj.background_tasks.BackgroundTasks.get_instance())
		PySide6.QtQml.qmlRegisterType(lyndj.music_directory.MusicDirectory, "Lyn", 1, 0, "MusicDirectory")
		PySide6.QtQml.qmlRegisterType(lyndj.waypoints_timeline.WaypointsTimeline, "Lyn", 1, 0, "WaypointsTimeline")

		logging.debug("Loading QML engine.")
		os.environ["QSG_RENDER_LOOP"] = "basic"  # QTBUG-58885: Animation speeds not accurate (which makes the track progress bar inaccurate).
		self.engine = PySide6.QtQml.QQmlApplicationEngine()
		self.engine.quit.connect(self.quit)
		self.engine.load("gui/MainWindow.qml")

		# Icon needs to be added AFTER the main window is loaded.
		self.setWindowIcon(PySide6.QtGui.QIcon(os.path.join(lyndj.storage.source(), "icon.svg")))

		logging.info("Start-up complete.")

	def create_gui_preferences(self):
		"""
		Creates preferences that are used in the GUI.

		The QML can't create new preferences. While the scope of the GUI would claim these preferences for themselves,
		it can't be defined there. We should define them here instead.
		"""
		prefs = lyndj.preferences.Preferences.getInstance()
		prefs.add("window/width", 1280)
		prefs.add("window/height", 720)
		prefs.add("window/x", 100)
		prefs.add("window/y", 100)
		prefs.add("window/visibility", "normal")
		prefs.add("divider_pos", 0.5)  # As a fraction of the width of the window.
		prefs.add("playlist/end_time", "23:00")
		prefs.add("autodj/enabled", True)
		prefs.add("autodj/energy", 50)
		prefs.add("autodj/age_variation", 10)
		prefs.add("autodj/style_variation", 10)
		prefs.add("autodj/energy_variation", 10)
		prefs.add("autodj/bpm_cadence", "120,150,120,180")
		prefs.add("autodj/bpm_precision", 0.2)
		prefs.add("autodj/energy_slider_power", 0.5)
		prefs.add("autodj/last_played_influence", 1.0)

	@PySide6.QtCore.Slot()
	def closing(self) -> None:
		"""
		Triggered when the main window is closed.
		"""
		lyndj.metadata.store()  # Write any last changes to disk.
		lyndj.player.Player.control_thread = None