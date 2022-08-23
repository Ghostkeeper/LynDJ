# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import os  # To list files in the music directory.
import os.path  # To list file paths in the music directory.
import PySide6.QtCore  # To expose this list to QML.

import metadata  # To get information about the files in the music directory.
import sorting  # To invert a sorting order.

class MusicDirectory(PySide6.QtCore.QAbstractTableModel):
	"""
	A list of the tracks contained within a certain directory, and their metadata.
	"""

	def __init__(self, parent=None):
		"""
		Construct a new music directory table.
		:param parent: The parent element to this QML element, if any.
		"""
		super().__init__(parent)

		self.column_fields = ["title", "author", "duration", "bpm", "comment"]

		self._directory = ""
		self.sort_field = ["comment", "author", "duration", "title", "bpm"]  # You can sort multiple fields at the same time. These two lists are in order of priority.
		self.sort_direction = [False, False, False, False, False]  # For each sort order, whether it is descending (True) or ascending (False).
		self.music = []  # The actual data contained in this table.

	def rowCount(self, parent=PySide6.QtCore.QModelIndex()):
		"""
		Returns the number of music files in this table.
		:param parent: The parent to display the child entries under. This is a plain table, so no parent should be
		provided.
		:return: The number of music files in this table.
		"""
		if parent.isValid():
			return 0
		return len(self.music)

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
		:param index: The row index of the cell to give the data from.
		:param role: Which data to return for this cell. Defaults to the data displayed, which is the only data we
		store for a cell.
		:return: The data contained in that cell, as a string.
		"""
		if not index.isValid():
			return None  # Only valid indices return data.
		if role != PySide6.QtCore.Qt.DisplayRole:
			return None  # Only return for the display role.
		return str(self.music[index.row()][self.column_fields[index.column()]])

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
			return ["Title", "Author", "Duration", "BPM", "Comment"][section]
		elif orientation == PySide6.QtCore.Qt.Orientation.Vertical:
			return str(section)
		else:
			return None

	def sort(self, column, descending_order):
		"""
		Sort the table by a certain column number.
		:param column: The index of the column to sort by.
		:param descending_order: Whether to sort in ascending order (False) or descending order (True).
		"""
		field = self.column_fields[column]
		current_index = self.sort_field.index(field)  # Remove the old place in the sorting priority.
		del self.sort_field[current_index]
		del self.sort_direction[current_index]
		self.sort_field.insert(0, field)  # And then re-insert it in front, with the highest priority.
		self.sort_direction.insert(0, descending_order)

		# Now sort it according to that priority.
		self.resort()

	def resort(self):
		"""
		Re-sort the table according to the current sorting priority list.
		"""
		def sort_key(entry):
			"""
			Create a key for each element to be sorted by.
			:param entry: A metadata entry.
			:return: The value to sort this entry by.
			"""
			key = []
			for i in range(len(self.sort_field)):
				value = entry[self.sort_field[i]]
				if type(value) == str:
					value = value.lower()
				if self.sort_direction[i]:
					value = sorting.ReverseOrder(value)
				key.append(value)
			return key

		self.layoutAboutToBeChanged.emit(PySide6.QtCore.QModelIndex(), self.VerticalSortHint)
		self.music = list(sorted(self.music, sort_key))
		self.layoutChanged.emit(PySide6.QtCore.QModelIndex(), self.VerticalSortHint)

	def directory_set(self, new_directory) -> None:
		"""
		Change the current directory that this model is looking at.
		:param new_directory: A path to a directory to look at.
		"""
		if new_directory == self._directory:  # Didn't actually change.
			return
		if not os.path.exists(new_directory):  # User is probably still typing.
			return

		metadata.add_directory(new_directory)  # Make sure we have the metadata cached of all files in this new directory.
		files = set(filter(metadata.is_music_file, [os.path.join(new_directory, filename) for filename in os.listdir(new_directory)]))
		new_music = [metadata.metadata[path] for path in files]  # Prepare the music itself, so that the switch to the user appears as quickly as possible.

		# Remove all old data from the table. We're assuming that since the directory changed, all files will be different.
		self.beginRemoveRows(PySide6.QtCore.QModelIndex(), 0, len(self.music) - 1)
		self.music.clear()
		self.endRemoveRows()

		# Add the new data.
		self.beginInsertRows(PySide6.QtCore.QModelIndex(), 0, len(new_music))
		self.music.extend(new_music)
		self.endInsertRows()
		self.resort()  # In the same sorting order as what the table is currently configured at.

		self._directory = new_directory

	@PySide6.QtCore.Property(str, fset=directory_set)
	def directory(self) -> str:
		"""
		The current directory that this model is looking at.
		:return: The current directory that this model is looking at.
		"""
		return self._directory