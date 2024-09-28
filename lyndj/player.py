# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2024 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os.path  # To cache Fourier transform images.
import PySide6.QtCore  # Exposing the player to QML.
import time  # To track playtime.
import typing
import uuid  # To generate filenames for the Fourier transform cache.

import lyndj.fourier  # To display spectrograph images for the user.
import lyndj.metadata  # To find or generate the Fourier transform image.
import lyndj.music_control  # To control the currently playing track.
import lyndj.playback  # To actually play the music.
import lyndj.preferences  # To get the playlist.
import lyndj.storage  # To cache Fourier transform images.
import lyndj.sound  # To store the audio we're playing.

class Player(PySide6.QtCore.QObject):
	"""
	An object that is responsible for playing music files, controlling how they're played (pause, play, volume,
	equaliser, etc.) and exporting information on what is playing (track and progress).

	This object only has class methods. All of the state is static and global, to prevent collisions with the underlying
	media APIs. The only reason it is an object is to expose the methods to QML easily so that they can be controlled
	from there.
	"""

	instance: typing.Optional["Player"] = None
	"""
	This class is a singleton. This stores the one instance that is allowed to exist.
	"""

	current_track: typing.Optional["lyndj.sound.Sound"] = None
	"""
	If a song is playing, this holds the currently playing track.

	If no song is playing, this is ``None``.
	"""

	control_track: typing.Optional[lyndj.music_control.MusicControl] = None
	"""
	If a song is playing, this holds an object that controls playback of the current track.

	This object controls volume, equalizer, and so on for the current track.
	"""

	start_time: typing.Optional[float] = None
	"""
	The time when the current track started playing. This can be used to determine the current playtime.

	If no track is playing, this should be set to ``None``.
	"""

	main_volume = 0.5
	"""
	The master volume control to play music at.
	"""

	is_mono = False
	"""
	Whether to convert the output audio to mono.

	Conversion to mono may help if some of the speakers aren't connected properly in the room.
	"""

	@classmethod
	def get_instance(cls) -> "Player":
		"""
		Get the single instance of this class, or create it if it wasn't created yet.
		:return: The instance of this class.
		"""
		if cls.instance is None:
			cls.instance = Player()
		return cls.instance

	def __init__(self, parent: typing.Optional[PySide6.QtCore.QObject]=None) -> None:
		"""
		Ensures that a few global things are properly initialised before using this class.
		:param parent: A parent Qt Object that this object is a child of.
		"""
		super().__init__(parent)
		prefs = lyndj.preferences.Preferences.get_instance()
		if not prefs.has("player/fadeout"):
			prefs.add("player/fadeout", 2.0)  # Fade-out for 2 seconds by default.
		if not prefs.has("player/fourier_samples"):
			prefs.add("player/fourier_samples", 2048)  # Number of samples of the Fourier image (horizontal).
		if not prefs.has("player/fourier_channels"):
			prefs.add("player/fourier_channels", 256)  # Resolution of the samples of the Fourier image (vertical).
		if not prefs.has("player/fourier_gamma"):
			prefs.add("player/fourier_gamma", 1.5)  # Gamma correction factor for Fourier images.
		if not prefs.has("player/silence"):
			prefs.add("player/silence", 2.0)  # 2 seconds silence between songs by default.
		if not prefs.has("player/mono"):
			prefs.add("player/mono", False)  # Whether to play audio in mono or not.
		if not prefs.has("player/buffer_size"):
			prefs.add("player/buffer_size", 10)  # Size of chunks to send to audio server, in ms. Larger chunks are more efficient, but cause greater delays.

		Player.is_mono = prefs.get("player/mono")

		self.song_finished.connect(self.mark_song_played)

	is_playing_changed = PySide6.QtCore.Signal()
	"""
	Triggered when the music is started or stopped.
	"""

	def is_playing_set(self, new_is_playing: bool) -> None:
		"""
		Start or stop the music.
		:param new_is_playing: Whether the music should be playing or not.
		"""
		if Player.current_track is None and new_is_playing:
			self.play_next()
		elif Player.current_track is not None and not new_is_playing:
			logging.info(f"Stopping playback.")
			self.control_track.fadeout(lyndj.preferences.Preferences.get_instance().get("player/fadeout"))
			if not lyndj.preferences.Preferences.get_instance().get("playlist/playlist")[0].startswith(":"):
				if (time.time() - Player.start_time) / self.current_duration > 0.5:  # Count it as "played" if we're over halfway through the track.
					self.song_finished.emit(lyndj.preferences.Preferences.get_instance().get("playlist/playlist")[0])
			Player.current_track = None
			Player.start_time = None
		self.is_playing_changed.emit()

	@PySide6.QtCore.Property(bool, fset=is_playing_set, notify=is_playing_changed)
	def is_playing(self) -> bool:
		"""
		Get whether the music is currently playing, or should be playing.

		If the music is paused, it is considered to be playing too. Only when it is stopped is it considered to not be
		playing.
		:return: ``True`` if the music is currently playing, or ``False`` if it is stopped.
		"""
		return Player.current_track is not None

	def play_next(self) -> None:
		"""
		Play the next song in the playlist.
		"""
		current_playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		if len(current_playlist) == 0:  # Nothing left in the playlist.
			self.is_playing_set(False)
			return

		# Cancel any upcoming events.
		if Player.control_track:
			Player.control_track.stop()

		next_song = current_playlist[0]
		logging.info(f"Starting playback of track: {next_song}")

		if next_song == ":pause:":
			self.is_playing_set(False)  # Stop playing.
			current_playlist = current_playlist[1:]  # Remove it from the playlist immediately.
			lyndj.preferences.Preferences.get_instance().set("playlist/playlist", current_playlist)
			return

		Player.current_track = lyndj.sound.Sound.decode(next_song)

		cut_start = lyndj.metadata.get(next_song, "cut_start")
		cut_end = lyndj.metadata.get(next_song, "cut_end")
		if cut_start == -1 or cut_start is None or cut_end == -1 or cut_end is None:  # Not trimmed yet.
			cut_start, cut_end = Player.current_track.detect_silence()
			lyndj.metadata.change(next_song, "cut_start", cut_start)
			lyndj.metadata.change(next_song, "cut_end", cut_end)
			lyndj.metadata.change(next_song, "duration", cut_end - cut_start)

		Player.control_track = lyndj.music_control.MusicControl(next_song, Player.current_track, self)

		fourier_file = lyndj.metadata.get(next_song, "fourier")
		if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
			fourier = lyndj.fourier.generate_fourier(Player.current_track, next_song)
			filename = os.path.splitext(os.path.basename(next_song))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
			filepath = os.path.join(lyndj.storage.cache(), "fourier", filename)
			fourier.save(filepath)
			lyndj.metadata.change(next_song, "fourier", filepath)

		self.set_volume(0.5)  # Back to default for the next song.

		Player.start_time = time.time()
		lyndj.playback.current_position = cut_start
		self.song_changed.emit()  # We loaded up a new song.
		self.current_cut_start_changed.emit()
		lyndj.playback.end_position = cut_end
		self.current_cut_end_changed.emit()
		lyndj.playback.play(Player.current_track)
		Player.control_track.play()

	@PySide6.QtCore.Slot()
	def clear_fourier(self) -> None:
		"""
		Clear all cached Fourier images, causing them to be regenerated upon the next restart or the next time the songs
		get played.
		"""
		logging.info("Clearing all cached Fourier images.")
		directory = os.path.join(lyndj.storage.cache(), "fourier")
		for filename in os.listdir(directory):
			os.remove(os.path.join(directory, filename))

	@PySide6.QtCore.Slot()
	def clear_current_waypoints(self) -> None:
		"""
		Clear the waypoints of the currently showing song.

		If no song was showing, nothing happens.
		"""
		current_playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return
		current_path = current_playlist[0]
		logging.info(f"Clearing waypoints for {current_path}")
		lyndj.metadata.change(current_path, "volume_waypoints", "")

	song_finished = PySide6.QtCore.Signal(str)
	"""
	Emitted when a song has finished playing or is stopped towards the end of the track.

	The parameter is the path to the song that had completed playing.
	"""

	def mark_song_played(self, path: str) -> None:
		"""
		Mark that the current song was recently played.
		:param path: The path to the song that was played.
		"""
		lyndj.metadata.change(path, "last_played", time.time())

	song_changed = PySide6.QtCore.Signal()
	"""
	Triggered when the currently playing song changes.
	"""

	@PySide6.QtCore.Property(PySide6.QtCore.QUrl, notify=song_changed)
	def current_fourier(self) -> PySide6.QtCore.QUrl:
		"""
		Get the path to the currently playing song's Fourier image.
		:return: A path to an image.
		"""
		current_playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return PySide6.QtCore.QUrl()
		if current_playlist[0] == ":pause:":
			return PySide6.QtCore.QUrl()
		current_path = current_playlist[0]
		fourier_path = lyndj.metadata.get(current_path, "fourier")
		return PySide6.QtCore.QUrl.fromLocalFile(fourier_path)

	current_cut_start_changed = PySide6.QtCore.Signal()
	"""
	Triggered when the song changes as well as when the current start cut changes.
	"""

	def set_current_cut_start(self, new_cut_start: float) -> None:
		"""
		Change the start cut position of the current song.
		:param new_cut_start: The new start cut position.
		"""
		if Player.current_track is None:
			return  # No track to change.
		current_path = self.currentPath
		if new_cut_start != lyndj.metadata.get(current_path, "cut_start"):
			lyndj.metadata.change(current_path, "cut_start", new_cut_start)
		self.current_cut_start_changed.emit()

	@PySide6.QtCore.Property(float, fset=set_current_cut_start, notify=current_cut_start_changed)
	def current_cut_start(self) -> float:
		"""
		Get the start cut position of the current song, in seconds.

		Before this position in the song, silence was detected.

		If there is no current song playing, this returns 0.
		:return: The timestamp of the start of the song.
		"""
		if Player.current_track is None:
			return 0
		current_path = self.currentPath
		return lyndj.metadata.get(current_path, "cut_start")

	current_cut_end_changed = PySide6.QtCore.Signal()
	"""
	Triggered when the song changes as well as when the current end cut changes.
	"""

	def set_current_cut_end(self, new_cut_end: float) -> None:
		"""
		Change the end cut position of the current song.
		:param new_cut_end: The new end cut position.
		"""
		if Player.current_track is None:
			return  # No track to change.
		current_path = self.currentPath
		if lyndj.metadata.get(current_path, "cut_end") == new_cut_end:  # No change.
			return
		lyndj.metadata.change(current_path, "cut_end", new_cut_end)  # Change the metadata for next time.
		if new_cut_end < lyndj.playback.current_position:  # Cut is moved before our current playback. Stop immediately.
			self.play_next()
		else:
			lyndj.playback.end_position = new_cut_end  # Change the end position in the playback so that the sound stops.
			Player.control_track.set_song_ends(new_cut_end - lyndj.playback.current_position)  # In the music control track, adjust the song-ends event so that the next song plays.
			self.current_cut_end_changed.emit()

	@PySide6.QtCore.Property(float, fset=set_current_cut_end, notify=current_cut_end_changed)
	def current_cut_end(self) -> float:
		"""
		Get the end cut position of the current song, in seconds.

		After this position in the song, silence was detected.

		If there is no current song playing, this returns 0.
		:return: The timestamp of the end of the song.
		"""
		if Player.current_track is None:
			return 0
		current_path = self.currentPath
		return lyndj.metadata.get(current_path, "cut_end")

	@PySide6.QtCore.Property(float, notify=song_changed)
	def current_duration(self) -> float:
		"""
		Get the duration of the current song, in seconds.

		If there is no current song playing, this returns 0.
		:return: The duration of the current song, in seconds.
		"""
		return self.current_cut_end - self.current_cut_start

	@PySide6.QtCore.Property(float, notify=song_changed)
	def current_total_duration(self) -> float:
		"""
		Get the duration of the current song in its original form, without being cut, in seconds.

		If there is no current song playing, this returns 0.
		:return: The duration of the current song without being cut, in seconds.
		"""
		if Player.current_track is None:
			return 0
		return Player.current_track.duration()

	@PySide6.QtCore.Slot(result=float)
	def current_progress(self) -> float:
		"""
		Get the current song's progress, as a fraction between 0 (the song just started) and 1 (the song completed).

		The start and end cuts of the song are not taken into account. If they change, this progress will not be changed
		along. This is necessary since the cut positions may change during the playback of the song, but the progress
		bar must remain stable.

		If there is no current song playing, this returns -1.
		:return: The current song's progress.
		"""
		if Player.current_track is None:
			return -1
		return lyndj.playback.current_position / self.current_total_duration

	@PySide6.QtCore.Property(str, notify=song_changed)
	def current_title(self) -> str:
		"""
		Get the title of the current song.
		:return: The title of the currently playing song.
		"""
		current_playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return ""
		if current_playlist[0] == ":pause:":
			return "Paused"
		current_path = current_playlist[0]  # Don't request from the playlist, which may be outdated. Get directly from metadata.
		return lyndj.metadata.get(current_path, "title")

	@PySide6.QtCore.Property(str, notify=song_changed)
	def currentPath(self) -> str:
		"""
		Get the path to the current song.
		:return: The path of the currently playing song.
		"""
		current_playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return ""
		return current_playlist[0]

	volume_changed = PySide6.QtCore.Signal()
	"""
	Triggered when something changes the playback volume of the current song.
	"""

	def set_volume(self, value: float) -> None:
		"""
		Changes the master volume to play music at.
		:param value: The new volume, between 0 and 1.
		"""
		if Player.main_volume != value:
			Player.main_volume = value
			self.volume_changed.emit()

	@PySide6.QtCore.Property(float, fset=set_volume, notify=volume_changed)
	def volume(self) -> float:
		"""
		The master volume control. This property determines how loud to play the music.
		:return: The current volume level.
		"""
		return Player.main_volume

	mono_changed = PySide6.QtCore.Signal()
	"""
	Triggered when something changes between mono and stereo.
	"""

	def set_mono(self, value: bool) -> None:
		"""
		Changes the mono toggle.
		:param value: The new value, whether to play mono (True) or stereo (False).
		"""
		if Player.is_mono != value:
			Player.is_mono = value
			lyndj.preferences.Preferences.get_instance().set("player/mono", value)
			self.mono_changed.emit()

	@PySide6.QtCore.Property(bool, fset=set_mono, notify=mono_changed)
	def mono(self) -> bool:
		"""
		Whether to play mono or not.

		If playing mono (True), all output channels will have the same audio data.
		If not playing mono (False), the original output channels of the audio will be retained.
		:return: Whether to play mono (True) or not (False).
		"""
		return Player.is_mono