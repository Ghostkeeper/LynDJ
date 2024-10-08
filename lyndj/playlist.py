# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2024 Ghostkeeper
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
import typing

import lyndj.autodj  # To suggest songs to add to the playlist.
import lyndj.metadata  # To show file metadata in the playlist table.
import lyndj.player  # To call upon the player to pre-load tracks.
import lyndj.preferences  # To store the playlist between restarts.
import lyndj.theme  # To get the colours for the BPM indication.

class Playlist(PySide6.QtCore.QAbstractListModel):
	"""
	A list of the tracks that are about to be played.

	This object is a singleton. There can only be one playlist. That way there is no confusion as to which playlist the
	player is taking tracks from.
	"""

	instance: typing.Optional["Playlist"] = None
	"""
	This class is a singleton. This stores the one instance that is allowed to exist.
	"""

	@classmethod
	def get_instance(cls) -> "Playlist":
		"""
		Gets the singleton instance. If no instance was made yet, it will be instantiated here.
		:return: The single instance of this class.
		"""
		if cls.instance is None:
			cls.instance = Playlist()
		return cls.instance

	def __init__(self, parent: typing.Optional[PySide6.QtCore.QObject]=None) -> None:
		"""
		Construct the instance of this class.
		:param parent: If this instance is created in a QML scene, the parent QML element.
		"""
		super().__init__(parent)

		prefs = lyndj.preferences.Preferences.get_instance()
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
		prefs = lyndj.preferences.Preferences.get_instance()
		paths = copy.copy(prefs.get("playlist/playlist"))
		suggested_track = ""
		if prefs.get("autodj/enabled"):
			suggested_track = lyndj.autodj.AutoDJ().suggested_track()
			if suggested_track != "":
				paths.append(suggested_track)
				if len(paths) == 1:  # If this is the only track in the playlist, actually go and add it to the playlist for real.
					prefs.get("playlist/playlist").append(suggested_track)
					logging.info(f"The playlist is empty. Auto-playing suggested track: {suggested_track}")
					# And then give a new suggestion.
					suggested_track = lyndj.autodj.AutoDJ().suggested_track()
					if suggested_track != "":
						paths.append(suggested_track)
		for path in paths:
			if path == ":pause:":
				file_metadata = {
					"duration": 0,
					"title": "(Pause playback)",
					"path": ":pause:",
					"comment": "Pause music playback when reaching this point in the playlist.",
					"bpm": 0,
				}
			else:
				if not lyndj.metadata.has(path):
					lyndj.metadata.add_file(path)
				file_metadata = copy.copy(lyndj.metadata.metadata[path])  # Make a copy that we can add information to.
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

		inserted_rows = False
		removed_rows = False
		if len(new_track_data) > len(self.track_data):
			self.beginInsertRows(PySide6.QtCore.QModelIndex(), len(self.track_data), len(new_track_data) - 1)
			inserted_rows = True
		elif len(new_track_data) < len(self.track_data):
			self.beginRemoveRows(PySide6.QtCore.QModelIndex(), len(new_track_data), len(self.track_data) - 1)
			removed_rows = True
		self.track_data = new_track_data
		if inserted_rows:
			self.endInsertRows()
		if removed_rows:
			self.endRemoveRows()
		self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.track_data), 0))

	def preferences_changed(self, key: str) -> None:
		"""
		Triggered if the preferences change, which means that this model has to update its data.
		:param key: The preference key that changed.
		"""
		if key in {
			"directory/browse_path",
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

	def metadata_changed(self, key: str) -> None:
		"""
		Triggered if a track's metadata changes, which means that this model has to update its data in order to possibly
		suggest a different track through the AutoDJ.
		:param key: The metadata key that was changed.
		"""
		if key in {
			"age",
			"style",
			"energy",
			"bpm",
			"last_played",
			"autodj_exclude",
		}:
			self.update()  # The AutoDJ-influencing fields changed, which may influence our decision for which track to suggest.

	def rowCount(self, parent: typing.Optional[PySide6.QtCore.QModelIndex]=PySide6.QtCore.QModelIndex()) -> int:
		"""
		Returns the number of music files in the playlist.
		:param parent: The parent to display the child entries under. This is a plain list, so no parent should be
		provided.
		:return: The number of music files in this playlist.
		"""
		if parent.isValid():
			return 0
		return len(self.track_data)

	def columnCount(self, parent: typing.Optional[PySide6.QtCore.QModelIndex]=PySide6.QtCore.QModelIndex()) -> int:
		"""
		Returns the number of metadata entries we're displaying in the table.
		:param parent: The parent to display the child entries under. This is a plain table, so no parent should be
		provided.
		:return: The number of metadata entries we're displaying in the table.
		"""
		if parent.isValid():
			return 0
		return 1

	def roleNames(self) -> typing.Dict[int, bytes]:
		"""
		Gets the names of the roles as exposed to QML.

		This function is called internally by Qt to match a model field in the QML code with the roles in this model.
		:return: A mapping of roles to field names. The field names are bytes.
		"""
		return {role: field.encode("utf-8") for role, field in self.role_to_field.items()}

	def data(self, index: PySide6.QtCore.QModelIndex, role: int=PySide6.QtCore.Qt.DisplayRole) -> typing.Any:
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
			theme_inst = lyndj.theme.Theme.get_instance()
			slow = theme_inst.colours["tempo_slow"]
			slow_rgba = [slow.red(), slow.green(), slow.blue(), slow.alpha()]
			medium = theme_inst.colours["tempo_medium"]
			medium_rgba = [medium.red(), medium.green(), medium.blue(), medium.alpha()]
			fast = theme_inst.colours["tempo_fast"]
			fast_rgba = [fast.red(), fast.green(), fast.blue(), fast.alpha()]
			prefs = lyndj.preferences.Preferences.get_instance()
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
	def add(self, path: str) -> None:
		"""
		Add a certain file to the playlist.
		:param path: The path to the file to add.
		"""
		# If the file is already in the playlist, do nothing.
		prefs = lyndj.preferences.Preferences.get_instance()
		playlist = prefs.get("playlist/playlist")
		if path in playlist:
			logging.debug(f"Tried adding {path} to the playlist, but it's already in the playlist.")
			return

		logging.info(f"Adding {path} to the playlist.")
		playlist.append(path)
		prefs.changed_internally("playlist/playlist")  # Trigger everything to update, including self.track_data.
		self.playlist_changed.emit()

	@PySide6.QtCore.Slot(int)
	def remove(self, index: int) -> None:
		"""
		Remove a certain file from the playlist.
		:param index: The position of the file to remove.
		"""
		prefs = lyndj.preferences.Preferences.get_instance()
		playlist = prefs.get("playlist/playlist")
		if index < 0 or index >= len(playlist):
			logging.error(f"Trying to remove playlist entry {index}, which is out of range.")
			return

		logging.info(f"Removing {playlist[index]} from the playlist.")
		playlist.pop(index)
		prefs.changed_internally("playlist/playlist")
		self.playlist_changed.emit()

	@PySide6.QtCore.Slot(str, int)
	def reorder(self, path: str, new_index: int) -> None:
		"""
		Move a certain file to a certain position in the playlist.

		If the file is not currently in the playlist, nothing will happen. It only reorders existing items.

		This will cause the file to be repositioned. The length of the playlist will not change.
		:param path: The path of the file to reorder.
		:param new_index: The new position of the file.
		"""
		prefs = lyndj.preferences.Preferences.get_instance()
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
	def playlist_endtime(self) -> float:
		"""
		Get the proposed endtime of the DJ session, as configured by the user.
		:return: The endtime in number of seconds since the Unix epoch.
		"""
		# Parse from the preference first.
		endtime_str = lyndj.preferences.Preferences.get_instance().get("playlist/end_time")
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
		if not lyndj.preferences.Preferences.get_instance().get("autodj/enabled"):
			return False
		return self.track_data[-1]["suggested"]

	def cumulative_update(self) -> None:
		"""
		Updates the cumulative duration timer with the currently remaining times.
		"""
		cumulative_endtime = time.time()

		if lyndj.player.Player.start_time is None:
			cumulative_duration = 0
		else:
			cumulative_duration = lyndj.player.Player.start_time - cumulative_endtime  # Start off with the negative current playtime.
			cumulative_endtime = lyndj.player.Player.start_time

		for track in self.track_data:
			duration = track["duration"]
			cumulative_endtime += duration
			track["cumulative_endtime"] = cumulative_endtime
			cumulative_duration += duration
			track["cumulative_duration"] = cumulative_duration
		self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(len(self.track_data), 0))