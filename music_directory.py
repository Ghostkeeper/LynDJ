# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import os  # To list files in the music directory.
import os.path  # To list file paths in the music directory.
import PySide6.QtCore  # To expose this list to QML.
import threading  # To update the metadata in downtime.
import typing

import metadata  # To get information about the files in the music directory.

class MusicDirectory(PySide6.QtCore.QAbstractListModel):
	"""
	A list of the tracks contained within a certain directory, and their metadata.
	"""

	def __init__(self, parent=None):
		"""
		Construct a new directory model.
		:param parent: The QML element to shove this under. If the parent is destroyed, this model is also freed.
		"""
		super().__init__(parent)

		user_role = PySide6.QtCore.Qt.ItemDataRole.UserRole
		self.roles = {
			b"filepath": user_role + 1,
			b"title": user_role + 2,
			b"author": user_role + 3,
			b"comment": user_role + 4,
			b"duration": user_role + 5,
			b"bpm": user_role + 6
		}
		self._directory = ""
		self._data = []
		self.update_thread = None
		self.sorted_role = self.roles[b"title"]

	def directory_set(self, new_directory) -> None:
		"""
		Change the current directory that this model is looking at.
		:param new_directory: A path to a directory to look at.
		"""
		if new_directory == self._directory:  # Didn't actually change.
			return
		if not os.path.exists(new_directory):  # User is probably still typing.
			return

		if self.update_thread is not None:  # A thread is already running to update metadata.
			thread = self.update_thread
			self.update_thread = None  # Signal to the thread that it should abort.
			thread.join()
		self._directory = new_directory
		self.update()
		self.update_thread = threading.Thread(target=self.update_metadata_task)
		self.update_thread.start()

	@PySide6.QtCore.Property(str, fset=directory_set)
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

	def is_music_file(self, path) -> bool:
		"""
		Returns whether the given file is a music file that we can read.
		:param path: The file to check.
		:return: ``True`` if it is a music track, or ``False`` if it isn't.
		"""
		path = os.path.join(self._directory, path)
		if not os.path.isfile(path):
			return False  # Only read files.
		ext = os.path.splitext(path)[1]
		return ext in [".mp3", ".flac", ".opus", ".ogg", ".wav"]  # Supported file formats.

	def update(self) -> None:
		"""
		Update the track list from the current contents of the watched directory.
		"""
		file_role = self.roles[b"filepath"]
		files = set(filter(self.is_music_file, os.listdir(self._directory)))
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
			self.beginRemoveRows(PySide6.QtCore.QModelIndex(), remove_pos, remove_pos)
			del self._data[remove_pos]
			self.endRemoveRows()

		for new_file in new_files:
			path = os.path.join(self._directory, new_file)
			metadata_dict = {
				self.roles[b"filepath"]: new_file,
				self.roles[b"title"]: metadata.get_cached(path, "title"),
				self.roles[b"author"]: metadata.get_cached(path, "author"),
				self.roles[b"comment"]: metadata.get_cached(path, "comment"),
				self.roles[b"duration"]: metadata.get_cached(path, "duration"),
				self.roles[b"bpm"]: metadata.get_cached(path, "bpm")
			}
			insert_pos = len(self._data)
			sorted_field = metadata_dict[self.sorted_role]
			if sorted_field is not None:
				for i in range(len(self._data)):
					other_field = self._data[i][self.sorted_role]
					if type(other_field) == str:
						if other_field.lower() > sorted_field.lower():  # Case-insensitive compare in case of strings.
							insert_pos = i
							break
					else:
						if other_field > sorted_field:
							insert_pos = i
							break
			self.beginInsertRows(PySide6.QtCore.QModelIndex(), insert_pos, insert_pos)
			self._data.insert(insert_pos, metadata_dict)
			self.endInsertRows()

	def update_metadata_task(self) -> None:
		"""
		A background task that gradually updates all of the metadata in the current folder.
		"""
		# We'll be modifying the data while iterating over it.
		# During this iteration, we have to keep the data sorted. To do this we'll re-insert the tracks into the list.
		# This may end up before the place where we're processing.
		# So to do this, we'll track an index manually, that we can increment if we're inserting above the cursor, or not if we're inserting below.
		cursor = 0
		while cursor < len(self._data):
			if self.update_thread is None:  # We have to abort.
				break
			entry = self._data[cursor]
			if entry[self.roles[b"title"]] is not None:  # Already processed.
				cursor += 1
				continue
			self.beginRemoveRows(PySide6.QtCore.QModelIndex(), cursor, cursor)
			self._data.pop(cursor)
			self.endRemoveRows()

			# Get the actual data from the file.
			path = os.path.join(self._directory, entry[self.roles[b"filepath"]])
			entry[self.roles[b"title"]] = metadata.get_entry(path, "title")
			entry[self.roles[b"author"]] = metadata.get_entry(path, "author")
			entry[self.roles[b"comment"]] = metadata.get_entry(path, "comment")
			entry[self.roles[b"duration"]] = metadata.get_entry(path, "duration")
			entry[self.roles[b"bpm"]] = metadata.get_entry(path, "bpm")

			# Find where to re-insert it, given the new information.
			insert_pos = len(self._data)
			sorted_field = entry[self.sorted_role]
			if sorted_field is not None:
				for i in range(len(self._data)):
					other_field = self._data[i][self.sorted_role]
					if other_field is None:
						continue
					if type(other_field) == str:
						if other_field.lower() > sorted_field.lower():  # Case-insensitive compare in case of strings.
							insert_pos = i
							break
					else:
						if other_field > sorted_field:
							insert_pos = i
							break
			if insert_pos <= cursor:  # If after the cursor, don't increment the cursor.
				cursor += 1
			self.beginInsertRows(PySide6.QtCore.QModelIndex(), insert_pos, insert_pos)
			self._data.insert(insert_pos, entry)
			self.endInsertRows()