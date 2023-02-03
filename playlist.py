# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import copy
import datetime  # To handle the DJ session end time.
import logging
import math  # To format durations.
import PySide6.QtCore  # To expose this list to QML.
import PySide6.QtGui  # To calculate display colours for song tempo.
import time  # To determine the remaining time until songs in the playlist start/end playing.

import autodj  # To suggest songs to add to the playlist.
import metadata  # To show file metadata in the playlist table.
import player  # To call upon the player to pre-load tracks.
import preferences  # To store the playlist between restarts.
import theme  # To get the colours for the BPM indication.

class Playlist(PySide6.QtCore.QAbstractListModel):
	"""
	A list of the tracks that are about to be played.

	This object is a singleton. There can only be one playlist. That way there is no confusion as to which playlist the
	player is taking tracks from.
	"""

	instance = None

	@classmethod
	def getInstance(cls):
		"""
		Gets the singleton instance. If no instance was made yet, it will be instantiated here.
		:return: The single instance of this class.
		"""
		if cls.instance is None:
			cls.instance = Playlist()
		return cls.instance

	def __init__(self, parent=None):
		super().__init__(parent)

		prefs = preferences.Preferences.getInstance()
		if not prefs.has("playlist/playlist"):
			prefs.add("playlist/playlist", [])
		prefs.add("playlist/slow_bpm", 100)
		prefs.add("playlist/medium_bpm", 150)
		prefs.add("playlist/fast_bpm", 220)

		user_role = PySide6.QtCore.Qt.UserRole
		self.role_to_field = {
			user_role + 1: "path",  # Path to the file.
			user_role + 2: "title",  # Title of the track.
			user_role + 3: "duration",  # Estimated duration of the track (before trimming silences).
			user_role + 4: "duration_seconds",  # The duration of this track, in seconds.
			user_role + 5: "bpm",  # Beats per minute, but as a colour scheme.
			user_role + 6: "comment",  # Any comment for the track.
			user_role + 7: "cumulative_duration",  # Time until this track has completed playing.
			user_role + 8: "cumulative_endtime",  # Timestamp of when the track has completed playing (seconds since epoch).
			user_role + 9: "suggested",  # Whether this track is user-added, or merely suggested by the application.
		}

		self.cumulative_update_timer = PySide6.QtCore.QTimer()
		self.cumulative_update_timer.setInterval(1000)  # Due to time drift it may sometimes skip a second. But this is such a small detail and it should be rare.
		self.cumulative_update_timer.timeout.connect(self.cumulative_update)
		self.cumulative_update_timer.start()

		self.track_data = []  # The source of data for the model.
		prefs.valuesChanged.connect(self.preferences_changed)
		self.update()

	def update(self) -> None:
		"""
		Fill the data in this model from the list of music track paths in the playlist.

		This will request the data for the files in the given list and fill the model with data.
		"""
		new_track_data = []
		prefs = preferences.Preferences.getInstance()
		paths = copy.copy(prefs.get("playlist/playlist"))
		suggested_track = ""
		added_double_suggested = False
		if prefs.get("autodj/enabled"):
			suggested_track = autodj.AutoDJ().suggested_track()
			if suggested_track != "":
				paths.append(suggested_track)
				if len(paths) == 1:  # If this is the only track in the playlist, actually go and add it to the playlist for real.
					prefs.get("playlist/playlist").append(suggested_track)
					# And then give a new suggestion.
					suggested_track = autodj.AutoDJ().suggested_track()
					if suggested_track != "":
						added_double_suggested = True
						paths.append(suggested_track)
		for path in paths:
			file_metadata = copy.copy(metadata.metadata[path])  # Make a copy that we can add information to.
			if len(new_track_data) == 0:
				file_metadata["cumulative_duration"] = file_metadata["duration"]
				file_metadata["cumulative_endtime"] = time.time() + file_metadata["duration"]
			else:
				file_metadata["cumulative_duration"] = new_track_data[len(new_track_data) - 1]["cumulative_duration"] + file_metadata["duration"]
				file_metadata["cumulative_endtime"] = new_track_data[len(new_track_data) - 1]["cumulative_endtime"] + file_metadata["duration"]
			file_metadata["duration_seconds"] = file_metadata["duration"]
			file_metadata["suggested"] = False  # Initially False. Set to True later for the one that is suggested.
			new_track_data.append(file_metadata)
		if suggested_track != "":
			new_track_data[-1]["suggested"] = True

		if added_double_suggested:
			self.beginInsertRows(PySide6.QtCore.QModelIndex(), len(new_track_data), len(new_track_data))
		self.track_data = new_track_data
		if added_double_suggested:
			self.endInsertRows()
		self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.track_data), 0))

	def preferences_changed(self, key):
		"""
		Triggered if the preferences change, which means that this model has to update its data.
		:param key: The preference key that changed.
		"""
		if key in {
			"playlist/playlist",
			"autodj/enabled",
			"autodj/energy",
			"autodj/age_variation",
			"autodj/style_variation",
			"autodj/energy_variation",
			"autodj/bpm_cadence",
			"autodj/bpm_precision",
			"autodj/energy_slider_power",
			"autodj/last_played_influence"
		}:
			self.update()  # The playlist changed, so update my model.

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
		if field == "duration" or field == "cumulative_duration":
			# Display duration as minutes:seconds.
			if value > 0:
				seconds = round(value)
				return str(math.floor(seconds / 60)) + ":" + ("0" if (seconds % 60 < 10) else "") + str(seconds % 60)
			else:
				return "0:00"
		if field == "bpm":
			# Display tempo as a colour!
			theme_inst = theme.Theme.getInstance()
			slow = theme_inst.colours["tempo_slow"]
			slow_rgba = [slow.red(), slow.green(), slow.blue(), slow.alpha()]
			medium = theme_inst.colours["tempo_medium"]
			medium_rgba = [medium.red(), medium.green(), medium.blue(), medium.alpha()]
			fast = theme_inst.colours["tempo_fast"]
			fast_rgba = [fast.red(), fast.green(), fast.blue(), fast.alpha()]
			prefs = preferences.Preferences.getInstance()
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
		if field == "suggested":
			# Return as boolean.
			return value
		return str(value)  # Default, just convert to string.

	@PySide6.QtCore.Slot(str)
	def add(self, path) -> None:
		"""
		Add a certain file to the playlist.
		:param path: The path to the file to add.
		"""
		# If the file is already in the playlist, do nothing.
		prefs = preferences.Preferences.getInstance()
		playlist = prefs.get("playlist/playlist")
		if path in playlist:
			logging.debug(f"Tried adding {path} to the playlist, but it's already in the playlist.")
			return

		logging.info(f"Adding {path} to the playlist.")
		self.beginInsertRows(PySide6.QtCore.QModelIndex(), len(playlist), len(playlist))
		playlist.append(path)
		prefs.changed_internally("playlist/playlist")  # Trigger everything to update, including self.track_data.
		self.endInsertRows()
		self.playlist_changed.emit()

	@PySide6.QtCore.Slot(int)
	def remove(self, index) -> None:
		"""
		Remove a certain file from the playlist.
		:param index: The position of the file to remove.
		"""
		prefs = preferences.Preferences.getInstance()
		playlist = prefs.get("playlist/playlist")
		if index < 0 or index >= len(playlist):
			logging.error(f"Trying to remove playlist entry {index}, which is out of range.")
			return

		logging.info(f"Removing {playlist[index]} from the playlist.")
		self.beginRemoveRows(PySide6.QtCore.QModelIndex(), index, index)
		playlist.pop(index)
		prefs.changed_internally("playlist/playlist")
		self.endRemoveRows()
		self.playlist_changed.emit()

	@PySide6.QtCore.Slot(str, int)
	def reorder(self, path, new_index) -> None:
		"""
		Move a certain file to a certain position in the playlist.

		If the file is not currently in the playlist, nothing will happen. It only reorders existing items.

		This will cause the file to be repositioned. The length of the playlist will not change.
		:param path: The path of the file to reorder.
		:param new_index: The new position of the file.
		"""
		prefs = preferences.Preferences.getInstance()
		playlist = prefs.get("playlist/playlist")
		try:
			old_index = playlist.index(path)
		except ValueError:  # File is not in the playlist.
			return

		logging.info(f"Move {path} to playlist index {new_index}")
		qt_new_index = new_index
		if old_index < new_index:
			qt_new_index += 1
		success = self.beginMoveRows(PySide6.QtCore.QModelIndex(), old_index, old_index, PySide6.QtCore.QModelIndex(), qt_new_index)
		if not success:
			logging.error(f"Attempt to move {path} out of range: {new_index}")
			return

		playlist.pop(old_index)
		playlist.insert(new_index, path)
		prefs.changed_internally("playlist/playlist")

		self.endMoveRows()
		self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.track_data), 0))
		self.playlist_changed.emit()

	@PySide6.QtCore.Slot(result="float")
	def playlist_endtime(self):
		"""
		Get the proposed endtime of the DJ session, as configured by the user.
		:return: The endtime in number of seconds since the Unix epoch.
		"""
		# Parse from the preference first.
		endtime_str = preferences.Preferences.getInstance().get("playlist/end_time")
		components = endtime_str.split(":")
		set_hours = int(components[0])
		set_minutes = int(components[1])

		# Let's guess whether the proposed end time is in the future or in the past.
		# If it's currently less than 4 hours after the end time, we'll consider it in the past.
		# If it's more than 4 hours after the end time, we'll consider it in the future (the time on the next day).
		now = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc)
		local_timezone = datetime.datetime.now().astimezone().tzinfo
		set_datetime = datetime.datetime(now.year, now.month, now.day, set_hours, set_minutes, 0, 0, tzinfo=local_timezone)
		if now - datetime.timedelta(seconds=4 * 3600) > set_datetime:  # Set datetime is more than 4 hours ago, so assume it's on the next day.
			set_datetime = set_datetime + datetime.timedelta(days=1)
		elif now + datetime.timedelta(seconds=20 * 3600) < set_datetime:  # Set date time is more than 20 hours in the future, so assume it's on the previous day.
			set_datetime = set_datetime - datetime.timedelta(days=1)

		return set_datetime.timestamp()

	playlist_changed = PySide6.QtCore.Signal()
	"""
	A signal triggered when something is changed in the playlist (added, removed or reordered).
	"""

	@PySide6.QtCore.Property(bool, notify=playlist_changed)
	def has_suggested_track(self) -> bool:
		"""
		Return whether this playlist has a suggested track at the end.

		If the AutoDJ is enabled and there are enough tracks in the playlist, there should pretty much always be a
		suggested track. But it is not guaranteed.
		"""
		if len(self.track_data) == 0:
			return False
		if not preferences.Preferences.getInstance().get("autodj/enabled"):
			return False
		return self.track_data[-1]["suggested"]

	def cumulative_update(self):
		"""
		Updates the cumulative duration timer with the currently remaining times.
		"""
		cumulative_endtime = time.time()

		if player.Player.start_time is None:
			cumulative_duration = 0
		else:
			cumulative_duration = player.Player.start_time - cumulative_endtime  # Start off with the negative current playtime.
			cumulative_endtime = player.Player.start_time

		for track in self.track_data:
			duration = track["duration"]
			cumulative_endtime += duration
			track["cumulative_endtime"] = cumulative_endtime
			cumulative_duration += duration
			track["cumulative_duration"] = cumulative_duration
		self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.track_data), 0))