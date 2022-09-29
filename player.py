# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import pygame  # The media player we're using to play music.
import PySide6.QtCore  # Exposing the player to QML.

import music_control  # To control the currently playing track.
import playlist  # To get the next track to play.
import preferences  # To get the playlist.
import threading  # To run the control thread.
import time  # To rate-limit the control track.

class Player(PySide6.QtCore.QObject):
	"""
	An object that is responsible for playing music files, controlling how they're played (pause, play, volume,
	equaliser, etc.) and exporting information on what is playing (track and progress).

	This object only has class methods. All of the state is static and global, to prevent collisions with the underlying
	media APIs. The only reason it is an object is to expose the methods to QML easily so that they can be controlled
	from there.
	"""

	current_track = None
	"""
	If a song is playing, this holds the currently playing track.

	If no song is playing, this is ``None``.
	"""

	control_track = None
	"""
	If a song is playing, this holds an object that controls playback of the current track.

	This object controls volume, equalizer, and so on for the current track.
	"""

	def __init__(self, parent=None) -> None:
		"""
		Ensures that a few global things are properly initialised before using this class.
		:param parent: A parent Qt Object that this object is a child of.
		"""
		super().__init__(parent)
		prefs = preferences.Preferences.getInstance()
		if not prefs.has("player/fadeout"):
			prefs.add("player/fadeout", 2.0)  # Fade-out for 2 seconds by default.

	is_playing_changed = PySide6.QtCore.Signal()

	def is_playing_set(self, new_is_playing) -> None:
		"""
		Start or stop the music.
		:param new_is_playing: Whether the music should be playing or not.
		"""
		if Player.current_track is None and new_is_playing:
			self.play_next()
		elif Player.current_track is not None and not new_is_playing:
			logging.info(f"Stopping playback.")
			Player.current_track.fadeout(round(preferences.Preferences.getInstance().get("player/fadeout") * 1000))  # Fade-out, convert to milliseconds for Pygame.
			Player.current_track = None
			Player.control_track.stop()
			Player.control_track = None
		self.is_playing_changed.emit()

	@PySide6.QtCore.Property(bool, fset=is_playing_set, notify=is_playing_changed)
	def isPlaying(self) -> bool:
		"""
		Get whether the music is currently playing, or should be playing.

		If the music is paused, it is considered to be playing too. Only when it is stopped is it considered to not be
		playing.
		:return: ``True`` if the music is currently playing, or ``False`` if it is stopped.
		"""
		return self.current_track is not None

	def play_next(self):
		"""
		Play the next song in the playlist.
		"""
		current_playlist = preferences.Preferences.getInstance().get("playlist/playlist")
		next_song = current_playlist[0]["path"]
		logging.info(f"Starting playback of track: {next_song}")
		Player.current_track = pygame.mixer.Sound(next_song)
		Player.control_track = music_control.MusicControl(next_song, Player.current_track, self)
		Player.current_track.play()
		Player.control_track.play()

		# Remove that track from the playlist.
		playlist.Playlist.getInstance().remove(0)