# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import os
import PyQt6.QtCore
import typing

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
		self._data = []

	def directory_set(self, new_directory) -> None:
		"""
		Change the current directory that this model is looking at.
		:param new_directory: A path to a directory to look at.
		"""
		self._directory = new_directory
		self.update()

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

	def update(self) -> None:
		"""
		Update the track list from the current contents of the watched directory.
		"""
		file_role = self.roles[b"filepath"]
		files = set(os.listdir(self._directory))
		old_files = set()
		for item in self._data:
			old_files.add(item[file_role])
		new_files = files - old_files
		removed_files = old_files - files

		for removed_file in removed_files:
			remove_pos = 0
			for i in range(len(self._data)):
				if self._data[i][file_role] == removed_file:
					remove_pos = i
			self.beginRemoveRows(PyQt6.QtCore.QModelIndex(), remove_pos, remove_pos)
			del self._data[remove_pos]
			self.endRemoveRows()

		for new_file in new_files:
			insert_pos = len(self._data)
			for i in range(len(self._data)):
				if self._data[i][file_role] < new_file:
					insert_pos = i
					break
			self.beginInsertRows(PyQt6.QtCore.QModelIndex(), insert_pos, insert_pos)
			self._data.insert(insert_pos, {
				self.roles[b"filepath"]: new_file,
				self.roles[b"title"]: "Test title",
				self.roles[b"author"]: "Test author",
				self.roles[b"duration"]: 180.0,
				self.roles[b"bpm"]: 140.0
			})
			self.endInsertRows()