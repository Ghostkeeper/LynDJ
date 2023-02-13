# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import math  # To format durations.
import PySide6.QtCore  # To expose this list to QML.
import PySide6.QtGui  # To calculate display colours for song tempo.

import lyndj.metadata  # To show file metadata in the playlist table.
import lyndj.player  # To trigger updates after the song changes.
import lyndj.preferences  # To store the playlist between restarts.
import lyndj.theme  # To get the colours for the BPM indication.

class History(PySide6.QtCore.QAbstractListModel):
	"""
	A list of the tracks that have been played in this session.

	This object is a singleton. There can only be one history. That way there is no confusion as to which history to
	display.
	"""

	instance = None

	@classmethod
	def getInstance(cls):
		"""
		Gets the singleton instance. If no instance was made yet, it will be instantiated here.
		:return: The single instance of this class.
		"""
		if cls.instance is None:
			cls.instance = History()
		return cls.instance

	def __init__(self, parent=None):
		super().__init__(parent)

		user_role = PySide6.QtCore.Qt.UserRole
		self.role_to_field = {
			user_role + 1: "path",  # Path to the file.
			user_role + 2: "title",  # Title of the track.
			user_role + 3: "duration",  # Estimated duration of the track (before trimming silences).
			user_role + 4: "bpm",  # Beats per minute, but as a colour scheme.
			user_role + 5: "comment",  # Any comment for the track.
		}

		self.track_data = []  # The source of data for the model.
		lyndj.player.Player.get_instance().song_finished.connect(self.add)  # Update the history when a song finished playing.

	def add(self, path) -> None:
		"""
		Add a track to the history.
		:param path: The path of the track to add to the history.
		"""
		if not lyndj.metadata.has(path):
			lyndj.metadata.add_file(path)

		self.beginInsertRows(PySide6.QtCore.QModelIndex(), len(self.track_data), len(self.track_data))
		self.track_data.append(lyndj.metadata.metadata[path])
		self.endInsertRows()

	def rowCount(self, parent=PySide6.QtCore.QModelIndex()):
		"""
		Returns the number of music files in the playlist.
		:param parent: The parent to display the child entries under. This is a plain list, so no parent should be
		provided.
		:return: The number of music files in this playlist.
		"""
		if parent.isValid():
			return 0
		return len(self.track_data)

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
		value = self.track_data[index.row()][field]
		if field == "duration":
			# Display duration as minutes:seconds.
			if value > 0:
				seconds = round(value)
				return str(math.floor(seconds / 60)) + ":" + ("0" if (seconds % 60 < 10) else "") + str(seconds % 60)
			else:
				return "0:00"
		if field == "bpm":
			# Display tempo as a colour!
			theme_inst = lyndj.theme.Theme.getInstance()
			slow = theme_inst.colours["tempo_slow"]
			slow_rgba = [slow.red(), slow.green(), slow.blue(), slow.alpha()]
			medium = theme_inst.colours["tempo_medium"]
			medium_rgba = [medium.red(), medium.green(), medium.blue(), medium.alpha()]
			fast = theme_inst.colours["tempo_fast"]
			fast_rgba = [fast.red(), fast.green(), fast.blue(), fast.alpha()]
			prefs = lyndj.preferences.Preferences.getInstance()
			slow_bpm = prefs.get("playlist/slow_bpm")
			medium_bpm = prefs.get("playlist/medium_bpm")
			fast_bpm = prefs.get("playlist/fast_bpm")

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