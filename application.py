# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import PyQt6.QtGui
import PyQt6.QtQml

class Application(PyQt6.QtGui.QGuiApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.engine = PyQt6.QtQml.QQmlApplicationEngine()
        self.engine.quit.connect(self.quit)
        self.engine.load("gui/MainWindow.qml")