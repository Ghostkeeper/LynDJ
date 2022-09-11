# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import copy
import logging
import math  # To format durations.
import PySide6.QtCore  # To expose this list to QML.
import PySide6.QtGui  # To calculate display colours for song tempo.

import metadata  # To show file metadata in the playlist table.
import theme  # To get the colours for the BPM indication.

class Playlist(PySide6.QtCore.QAbstractListModel):
	"""
	A list of the tracks that are about to be played.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		self.playlist = []  # The actual data contained in this table.

		user_role = PySide6.QtCore.Qt.UserRole
		self.role_to_field = {
			user_role + 1: "path",
			user_role + 2: "title",
			user_role + 3: "duration",
			user_role + 4: "bpm",
			user_role + 5: "comment",
			user_role + 6: "cumulative_duration"
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

	def roleNames(self):
		"""
		Gets the names of the roles as exposed to QML.

		This function is called internally by Qt to match a model field in the QML code with the roles in this model.
		:return: A mapping of roles to field names. The field names are bytes.
		"""
		return {role: field.encode("utf-8") for role, field in self.role_to_field.items()}

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
		if field == "duration" or field == "cumulative_duration":
			# Display duration as minutes:seconds.
			seconds = round(value)
			return str(math.floor(seconds / 60)) + ":" + ("0" if (seconds % 60 < 10) else "") + str(seconds % 60)
		if field == "bpm":
			# Display tempo as a colour!
			theme_inst = theme.Theme.getInstance()
			slow = theme_inst.colours["tempo_slow"]
			slow_rgba = [slow.red(), slow.green(), slow.blue(), slow.alpha()]
			medium = theme_inst.colours["tempo_medium"]
			medium_rgba = [medium.red(), medium.green(), medium.blue(), medium.alpha()]
			fast = theme_inst.colours["tempo_fast"]
			fast_rgba = [fast.red(), fast.green(), fast.blue(), fast.alpha()]
			slow_bpm = 100
			medium_bpm = 150
			fast_bpm = 220

			if value <= 0:  # No BPM information. Return neutral tempo.
				return medium
			if value < slow_bpm:  # The minimum tempo we'll consider. Completely slow.
				return slow
			if value < medium_bpm:  # The medium tempo. So between slow and medium we'll interpolate.
				interpolation = (value - slow_bpm) / (medium_bpm - slow_bpm)
				return PySide6.QtGui.QColor(*[interpolation * medium_rgba[i] + (1 - interpolation) * slow_rgba[i] for i in range(4)])
			if value < fast_bpm:  # The fast tempo. Between medium and fast we'll interpolate.
				interpolation = (value - medium_bpm) / (fast_bpm - medium_bpm)
				return PySide6.QtGui.QColor(*[interpolation * fast_rgba[i] + (1 - interpolation) * medium_rgba[i] for i in range(4)])
			# Above the fast tempo. Completely fast.
			return fast
		return str(value)  # Default, just convert to string.

	@PySide6.QtCore.Slot(str)
	def add(self, path) -> None:
		"""
		Add a certain file to the playlist.
		:param path: The path to the file to add.
		"""
		# If the file is already in the playlist, do nothing.
		for existing_file in self.playlist:
			if existing_file["path"] == path:
				logging.debug(f"Tried adding {path} to the playlist, but it's already in the playlist.")
				return

		file_metadata = copy.copy(metadata.metadata[path])  # Make a copy that we can add information to.
		if len(self.playlist) == 0:
			file_metadata["cumulative_duration"] = file_metadata["duration"]
		else:
			file_metadata["cumulative_duration"] = self.playlist[len(self.playlist) - 1]["cumulative_duration"] + file_metadata["duration"]

		logging.info(f"Adding {path} to the playlist.")
		self.beginInsertRows(PySide6.QtCore.QModelIndex(), len(self.playlist), len(self.playlist))
		self.playlist.append(file_metadata)
		self.endInsertRows()

	@PySide6.QtCore.Slot(str, int)
	def reorder(self, path, new_index) -> None:
		"""
		Move a certain file to a certain position in the playlist.

		If the file is not currently in the playlist, nothing will happen. It only reorders existing items.

		This will cause the file to be repositioned. The length of the playlist will not change.
		:param path: The path of the file to reorder.
		:param new_index: The new position of the file.
		"""
		for i, existing_file in enumerate(self.playlist):
			if existing_file["path"] == path:
				old_index = i
				break
		else:
			return  # The file is not in the playlist.

		logging.info(f"Move {path} to playlist index {new_index}")
		qt_new_index = new_index
		if old_index < new_index:
			qt_new_index += 1
		success = self.beginMoveRows(PySide6.QtCore.QModelIndex(), old_index, old_index, PySide6.QtCore.QModelIndex(), qt_new_index)
		if not success:
			logging.error(f"Attempt to move {path} out of range: {new_index}")
			return

		file_data = self.playlist[old_index]
		self.playlist.pop(old_index)
		self.playlist.insert(new_index, file_data)

		self.endMoveRows()

		# Update the cumulative durations in the part of the list that got changed.
		lower = min(old_index, new_index)
		upper = max(old_index, new_index)
		for i in range(lower, upper + 1):
			if i == 0:
				self.playlist[0]["cumulative_duration"] = self.playlist[0]["duration"]
			else:
				self.playlist[i]["cumulative_duration"] = self.playlist[i]["duration"] + self.playlist[i - 1]["cumulative_duration"]
		self.dataChanged.emit(self.createIndex(lower, 0), self.createIndex(upper, 0))