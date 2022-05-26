# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import PyQt6.QtGui
import PyQt6.QtQml

import preferences

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

        logging.debug("Registering QML types.")
        PyQt6.QtQml.qmlRegisterSingletonType(preferences.Preferences, "Lyn", 1, 0, preferences.Preferences.getInstance, "Preferences")

        logging.debug("Loading QML engine.")
        self.engine = PyQt6.QtQml.QQmlApplicationEngine()
        self.engine.quit.connect(self.quit)
        self.engine.load("gui/MainWindow.qml")

        logging.info("Start-up complete.")