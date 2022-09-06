# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import math  # To format durations.
import PySide6.QtCore  # To expose this table to QML.

import metadata  # To show file metadata in the playlist table.

class Playlist(PySide6.QtCore.QAbstractListModel):
	"""
	A list of the tracks that are about to be played.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		self.playlist = []  # The actual data contained in this table.

		self.column_fields = ["title", "duration", "bpm", "comment"]
		user_role = PySide6.QtCore.Qt.UserRole
		self.role_to_field = {
			user_role + 1: "title",
			user_role + 2: "duration",
			user_role + 3: "bpm",
			user_role + 4: "comment"
		}

	def rowCount(self, parent=PySide6.QtCore.QModelIndex()):
		"""
		Returns the number of music files in the playlist.
		:param parent: The parent to display the child entries under. This is a plain list, so no parent should be
		provided.
		:return: The number of music files in this playlist.
		"""
		if parent.isValid():
			return 0
		return len(self.playlist)

	def columnCount(self, parent=PySide6.QtCore.QModelIndex()):
		"""
		Returns the number of metadata entries we're displaying in the table.
		:param parent: The parent to display the child entries under. This is a plain table, so no parent should be
		provided.
		:return: The number of metadata entries we're displaying in the table.
		"""
		if parent.isValid():
			return 0
		return 1

	def data(self, index, role=PySide6.QtCore.Qt.DisplayRole):
		"""
		Returns one field of the data in the list.
		:param index: The row of the entry to return the data from.
		:param role: Which data to return for this cell.
		:return: The data contained in that cell, as a string.
		"""
		if not index.isValid():
			return None  # Only valid indices return data.
		if role not in self.role_to_field:
			return None
		field = self.role_to_field[role]
		value = self.playlist[index.row()][field]
		if field == "duration":
			# Display duration as minutes:seconds.
			seconds = round(value)
			return str(math.floor(seconds / 60)) + ":" + ("0" if (seconds % 60 < 10) else "") + str(seconds % 60)
		if field == "bpm":
			# Don't display negatives (= no information)
			if value <= 0:
				return ""
			return str(round(value))
		return str(value)  # Default, just convert to string.

	@PySide6.QtCore.Slot(str)
	def add(self, path) -> None:
		"""
		Add a certain file to the playlist.
		:param path: The path to the file to add.
		"""
		file_metadata = metadata.metadata[path]
		logging.info(f"Adding {path} to the playlist.")
		self.beginInsertRows(PySide6.QtCore.QModelIndex(), len(self.playlist), len(self.playlist))
		self.playlist.append(file_metadata)
		self.endInsertRows()