# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2024 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import math  # To format track duration.
import os  # To list files in the music directory.
import os.path  # To list file paths in the music directory.
import PySide6.QtCore  # To expose this table to QML, and get the standard music directory.
import time  # To display the last played time relative to the current time.
import typing

import lyndj.background_tasks  # To generate spectrograph images in the background.
import lyndj.fourier  # To generate spectrograph images in the background.
import lyndj.metadata  # To get information about the files in the music directory.
import lyndj.player  # To cache Fourier images of the tracks in this directory.
import lyndj.preferences  # To store the sorting order.
import lyndj.sorting  # To invert a sorting order.
import lyndj.sound  # To pre-process audio files.

class MusicDirectory(PySide6.QtCore.QAbstractTableModel):
	"""
	A list of the tracks contained within a certain directory, and their metadata.
	"""

	def __init__(self, parent: typing.Optional[PySide6.QtCore.QObject]=None) -> None:
		"""
		Construct a new music directory table.
		:param parent: The parent element to this QML element, if any.
		"""
		super().__init__(parent)

		self.column_fields = ["title", "author", "duration", "bpm", "comment", "last_played", "age", "style", "energy"]

		self._directory = ""
		prefs = lyndj.preferences.Preferences.get_instance()
		music_locations = PySide6.QtCore.QStandardPaths.standardLocations(PySide6.QtCore.QStandardPaths.StandardLocation.MusicLocation)
		if music_locations:
			browse_path = music_locations[0]
		else:
			browse_path = os.path.expanduser("~/")
		if not prefs.has("directory/browse_path"):
			prefs.add("directory/browse_path", browse_path)
		if not prefs.has("directory/sort_order"):
			prefs.add("directory/sort_order", ["bpm", "last_played", "age", "style", "energy", "title", "duration", "author", "comment"])  # You can sort multiple fields at the same time. These two lists are in order of priority.
		if not prefs.has("directory/sort_direction"):
			prefs.add("directory/sort_direction", [False, False, False, False, False, False, False, False, False])  # For each sort order, whether it is descending (True) or ascending (False).
		self.music: typing.List[typing.Dict[str, typing.Any]] = []  # The actual data contained in this table.

		if not prefs.has("directory/column_width"):
			fraction = 1.0 / len(self.column_fields)  # Equal fraction for each column.
			prefs.add("directory/column_width", [fraction, fraction, fraction, fraction, fraction, fraction, fraction, fraction, fraction])

	def rowCount(self, parent: typing.Optional[PySide6.QtCore.QModelIndex]=PySide6.QtCore.QModelIndex()) -> int:
		"""
		Returns the number of music files in this table.
		:param parent: The parent to display the child entries under. This is a plain table, so no parent should be
		provided.
		:return: The number of music files in this table.
		"""
		if parent.isValid():
			return 0
		return len(self.music)

	def columnCount(self, parent: typing.Optional[PySide6.QtCore.QModelIndex]=PySide6.QtCore.QModelIndex()) -> int:
		"""
		Returns the number of metadata entries we're displaying in the table.
		:param parent: The parent to display the child entries under. This is a plain table, so no parent should be
		provided.
		:return: The number of metadata entries we're displaying in the table.
		"""
		if parent.isValid():
			return 0
		return len(self.column_fields)

	def data(self, index: PySide6.QtCore.QModelIndex, role: int=PySide6.QtCore.Qt.DisplayRole) -> typing.Any:
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
		value = self.music[index.row()][field]
		if field == "duration":
			# Display duration as minutes:seconds.
			seconds = round(value)
			return str(math.floor(seconds / 60)) + ":" + ("0" if (seconds % 60 < 10) else "") + str(seconds % 60)
		if field == "bpm":
			# Don't display negatives (= no information)
			if value <= 0:
				return ""
			return str(round(value))
		if field == "last_played":
			# Not updated live, so we'll have pretty coarse resolution here.
			if value <= 0:
				return "Never"
			day = 60 * 60 * 24  # Amount of seconds in a day.
			difference = time.time() - value
			if difference < day / 2:
				return "Today"
			if difference < day * 1.5:
				return "Yesterday"
			return str(round(difference / day)) + " days"
		return str(value)  # Default, just convert to string.

	def flags(self, index: PySide6.QtCore.QModelIndex) -> int:
		"""
		Returns metadata properties of a cell.
		:param index: The cell to get metadata of.
		:return: The metadata flags for that cell.
		"""
		return PySide6.QtCore.Qt.ItemFlag.ItemIsSelectable | PySide6.QtCore.Qt.ItemFlag.ItemIsEnabled

	@PySide6.QtCore.Slot(int, int, int, result=str)
	def headerData(self, section: int, orientation: int, role: int=PySide6.QtCore.Qt.DisplayRole) -> typing.Optional[str]:
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
			return ["title", "author", "duration", "bpm", "comment", "last_played", "age", "style", "energy"][section]
		elif orientation == PySide6.QtCore.Qt.Orientation.Vertical:
			return self.music[section]["path"]
		else:
			return None

	@PySide6.QtCore.Slot(str, bool)
	def sort(self, column: typing.Union[int, str], descending_order: bool) -> None:
		"""
		Sort the table by a certain column number.
		:param column: The index of the column to sort by, or the role to sort by.
		:param descending_order: Whether to sort in ascending order (False) or descending order (True).
		"""
		logging.info(f"Sorting music directory by {column}, {'descending' if descending_order else 'ascending'}")
		if type(column) is int:
			column = self.column_fields[column]
		prefs = lyndj.preferences.Preferences.get_instance()
		sort_field = prefs.get("directory/sort_order")
		sort_direction = prefs.get("directory/sort_direction")
		current_index = sort_field.index(column)  # Remove the old place in the sorting priority.
		del sort_field[current_index]
		del sort_direction[current_index]
		sort_field.insert(0, column)  # And then re-insert it in front, with the highest priority.
		sort_direction.insert(0, descending_order)
		prefs.set("directory/sort_order", sort_field)
		prefs.set("directory/sort_direction", sort_direction)

		# Now sort it according to that priority.
		self.resort()

	def resort(self) -> None:
		"""
		Re-sort the table according to the current sorting priority list.
		"""
		prefs = lyndj.preferences.Preferences.get_instance()
		sort_field = prefs.get("directory/sort_order")
		sort_direction = prefs.get("directory/sort_direction")
		def sort_key(entry: typing.Dict[str, typing.Any]) -> typing.List[typing.Any]:
			"""
			Create a key for each element to be sorted by.
			:param entry: A metadata entry.
			:return: The value to sort this entry by.
			"""
			key = []
			for i in range(len(sort_field)):
				value = entry[sort_field[i]]
				if type(value) == str:
					value = value.lower()
				if sort_direction[i]:
					value = lyndj.sorting.ReverseOrder(value)
				key.append(value)
			return key

		self.layoutAboutToBeChanged.emit()
		self.music = list(sorted(self.music, key=sort_key))
		self.layoutChanged.emit()

	def directory_set(self, new_directory: str) -> None:
		"""
		Change the current directory that this model is looking at.
		:param new_directory: A path to a directory to look at.
		"""
		if new_directory == self._directory:  # Didn't actually change.
			return
		if not os.path.exists(new_directory):  # User is probably still typing.
			return

		lyndj.metadata.add_directory(new_directory)  # Make sure we have the metadata cached of all files in this new directory.
		files = set(filter(lyndj.metadata.is_music_file, [os.path.join(new_directory, filename) for filename in os.listdir(new_directory)]))
		new_music = [lyndj.metadata.metadata[path] for path in files]  # Prepare the music itself, so that the switch to the user appears as quickly as possible.

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

		# Add background tasks for pre-processing tracks.
		def preprocess(path: str) -> None:
			"""
			Pre-process a single track.
			:param path: The path to the audio file to pre-process.
			"""
			fourier_file = lyndj.metadata.get(path, "fourier")
			cut_start = lyndj.metadata.get(path, "cut_start")
			cut_end = lyndj.metadata.get(path, "cut_end")
			if fourier_file != "" and os.path.exists(fourier_file) and cut_start is not None and cut_start != -1 and cut_end is not None and cut_end != -1:
				return  # These were computed in the meanwhile. Perhaps the song played in the meanwhile.

			segment = lyndj.sound.Sound.decode(path)
			if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
				lyndj.fourier.generate_and_save_fourier(path, segment)
			if cut_start is None or cut_start == -1 or cut_end is None or cut_end == -1:
				cut_start, cut_end = segment.detect_silence()
				lyndj.metadata.change(path, "cut_start", cut_start)
				lyndj.metadata.change(path, "cut_end", cut_end)

		tasks = lyndj.background_tasks.BackgroundTasks.get_instance()
		for path in files:
			tasks.add(lambda p=path: preprocess(p), "Spectrograph and silence detection", allow_during_playback=False)

	@PySide6.QtCore.Property(str, fset=directory_set)
	def directory(self) -> str:
		"""
		The current directory that this model is looking at.
		:return: The current directory that this model is looking at.
		"""
		return self._directory

	@PySide6.QtCore.Slot(str, result="int")
	def is_sorted(self, field: str) -> int:
		"""
		Gives the sorting status of a field in the table.

		The sorting can be:
		* 1: The field is sorted in ascending order.
		* 0: The field is not sorted (not the highest priority anyway).
		* -1: The field is sorted in descending order.
		"""
		prefs = lyndj.preferences.Preferences.get_instance()
		if prefs.get("directory/sort_order")[0] != field:  # Not the highest priority sort.
			return 0
		if prefs.get("directory/sort_direction")[0]:  # Descending.
			return -1
		else:  # Ascending.
			return 1

	@PySide6.QtCore.Slot(int, result=str)
	def get_path(self, index: int) -> str:
		"""
		Get the path to the file at the given row in the table.
		:param index: A row number to get the file path of.
		:return: A path to the file on local disk.
		"""
		return self.music[index]["path"]

	@PySide6.QtCore.Slot(str, result=int)
	def get_row(self, path: str) -> int:
		"""
		Get the row number of a certain file, by the path to the file.

		If the file is not in this table, this returns -1.
		:param path: The path to the file to search.
		:return: The row index of that file, or -1 if the file is not in the table.
		"""
		for i in range(len(self.music)):
			if self.music[i]["path"] == path:
				return i
		else:
			return -1

	@PySide6.QtCore.Slot(str, str, str)
	def change_metadata(self, path: str, key: str, value: typing.Any) -> None:
		"""
		Change an individual metadata element of a file, and change it also inside of that file.

		This changes the metadata inside of the metadata tags of the music file, if applicable.
		:param path: The path to the file to change metadata of.
		:param key: The metadata entry to change.
		:param value: The new value for this metadata entry.
		"""
		lyndj.metadata.change(path, key, value)
		# Looking up where in the table the data changed is much more expensive than just triggering an update of the entire column.
		column = self.column_fields.index(key)
		self.dataChanged.emit(self.createIndex(0, column), self.createIndex(len(self.music) - 1, column))