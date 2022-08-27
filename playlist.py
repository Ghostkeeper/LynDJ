# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import math  # To format durations.
import PySide6.QtCore  # To expose this table to QML.

import metadata  # To show file metadata in the playlist table.
import preferences  # For the column widths.

class MusicDirectory(PySide6.QtCore.QAbstractTableModel):
	"""
	A list of the tracks that are about to be played.
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		self.column_fields = ["title", "duration", "bpm", "comment"]
		self.playlist = []  # The actual data contained in this table.

		prefs = preferences.Preferences.getInstance()
		if not prefs.has("playlist/column_width"):
			fraction = 1.0 / len(self.column_fields)  # Equal fraction for each column.
			prefs.add("playlist/column_width", [fraction, fraction, fraction, fraction, fraction])

	def rowCount(self, parent=PySide6.QtCore.QModelIndex()):
		"""
		Returns the number of music files in the playlist.
		:param parent: The parent to display the child entries under. This is a plain table, so no parent should be
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
		return len(self.column_fields)

	def data(self, index, role=PySide6.QtCore.Qt.DisplayRole):
		"""
		Returns one cell of the table.
		:param index: The row and column index of the cell to give the data from.
		:param role: Which data to return for this cell. Defaults to the data displayed, which is the only data we
		store for a cell.
		:return: The data contained in that cell, as a string.
		"""
		if not index.isValid():
			return None  # Only valid indices return data.
		if role != PySide6.QtCore.Qt.DisplayRole:
			return None  # Only return for the display role.
		field = self.column_fields[index.column()]
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

	def headerData(self, section, orientation, role):
		"""
		Returns the row or column labels for the table.

		This table doesn't really use any row labels. We'll return the row index, but it shouldn't get displayed.
		:param section: The row or column index.
		:param orientation: Whether to get the row labels or the column labels.
		:param role: Which data to return for the headers. Defaults to the data displayed, which is the only data we can
		return.
		:return: The header for the row or column, as a string.
		"""
		if role != PySide6.QtCore.Qt.DisplayRole:
			return None
		if orientation == PySide6.QtCore.Qt.Orientation.Horizontal:
			return ["Title", "Duration", "BPM", "Comment"][section]
		elif orientation == PySide6.QtCore.Qt.Orientation.Vertical:
			return str(section)
		else:
			return None

	@PySide6.QtCore.Slot(str)
	def add(self, path) -> None:
		"""
		Add a certain file to the playlist.
		:param path: The path to the file to add.
		"""
		file_metadata = metadata.metadata[path]
		self.playlist.append(file_metadata)