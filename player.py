# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import numpy  # For the Fourier transform in Scipy.
import pygame  # The media player we're using to play music.
import PySide6.QtCore  # Exposing the player to QML.
import PySide6.QtGui  # For the QImage to display the Fourier transform.
import scipy.fft  # For the Fourier transform.
import time  # To track playtime.

import music_control  # To control the currently playing track.
import preferences  # To get the playlist.

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

	start_time = None
	"""
	The time when the current track started playing. This can be used to determine the current playtime.

	If no track is playing, this should be set to ``None``.
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
		if not prefs.has("player/fourier_samples"):
			prefs.add("player/fourier_samples", 2048)  # Number of samples of the fourier image (horizontal).
		if not prefs.has("player/fourier_channels"):
			prefs.add("player/fourier_channels", 256)  # Resolution of the samples of the fourier image (vertical).

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
			Player.start_time = None
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
		self.generate_fourier(Player.current_track)  # TODO: Cache this.
		Player.control_track = music_control.MusicControl(next_song, Player.current_track, self)
		Player.start_time = time.time()
		Player.current_track.play()
		Player.control_track.play()

	def generate_fourier(self, sound):
		"""
		Generate an image of the fourier transform of a track.
		:param sound: A sound sample to generate the fourier transform from.
		:return: A QImage of the fourier transform of the given track.
		"""
		# Get the waveform and transform it into frequency space.
		waveform = sound.get_raw()
		prefs = preferences.Preferences.getInstance()
		num_chunks = prefs.get("player/fourier_samples")
		num_channels = prefs.get("player/fourier_channels")
		waveform_numpy = numpy.frombuffer(waveform, dtype=numpy.ubyte)[::2]  # Only take one channel of the (hopefully) stereo sound.
		chunks = numpy.array_split(waveform_numpy, num_chunks)
		transformed = numpy.zeros((num_chunks, num_channels), dtype=numpy.ubyte)  # Result array for the transformed chunks.
		for i, chunk in enumerate(chunks):
			fourier = scipy.fft.rfft(chunk)
			fourier = numpy.abs(fourier[0:len(fourier) // 2 // num_channels * num_channels])  # Ignore the top 50% of the image which repeats due to Nyquist.
			# Split the frequencies into ranges.
			# Then sum up those ranges to get the brightness for individual pixels.
			fourier_pixels = numpy.sum(numpy.array_split(fourier, num_channels), axis=1)
			# Scale to the range 0-256 for the image.
			max_value = numpy.max(fourier_pixels) / 256
			fourier_pixels /= max_value

			transformed[i] = fourier_pixels

		# Generate an image from it.
		transformed = numpy.transpose(transformed).copy()
		result = PySide6.QtGui.QImage(transformed, num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)
		#result.save("test.png")