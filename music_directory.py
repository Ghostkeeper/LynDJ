# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import PyQt6.QtCore
import typing

import track

class MusicDirectory(PyQt6.QtCore.QAbstractListModel):
	"""
	A list of the tracks contained within a certain directory, and their metadata.
	"""

	def __init__(self, parent=None):
		"""
		Construct a new directory model.
		:param parent: The QML element to shove this under. If the parent is destroyed, this model is also freed.
		"""
		super().__init__(parent)

		user_role = PyQt6.QtCore.Qt.ItemDataRole.UserRole
		self.roles = {
			b"filepath": user_role + 1,
			b"title": user_role + 2,
			b"author": user_role + 3,
			b"duration": user_role + 4,
			b"bpm": user_role + 5
		}
		self._directory = ""

	def directory_set(self, new_directory) -> None:
		"""
		Change the current directory that this model is looking at.
		:param new_directory: A path to a directory to look at.
		"""
		self._directory = new_directory

	@PyQt6.QtCore.pyqtProperty(str, fset=directory_set)
	def directory(self) -> str:
		"""
		The current directory that this model is looking at.
		:return: The current directory that this model is looking at.
		"""
		return self._directory

	def roleNames(self) -> typing.Dict[int, bytes]:
		return {role: name for name, role in self.roles.items()}  # Inverse of role dict.

	def rowCount(self, parent=None) -> int:
		return len(self._data)

	def data(self, index, role) -> typing.Any:
		return self._data[index.row()][role]

	"""
	Triggered when the list of tracks changes.
	"""
	tracksChanged = PyQt6.QtCore.pyqtSignal()