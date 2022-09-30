# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import math  # Transformations on the Fourier transform.
import mutagen  # To get metadata on the samples of the sound.
import numpy  # For the Fourier transform in Scipy.
import os.path  # To cache Fourier transform images.
import pygame  # The media player we're using to play music.
import PySide6.QtCore  # Exposing the player to QML.
import PySide6.QtGui  # For the QImage to display the Fourier transform.
import scipy.fft  # For the Fourier transform.
import time  # To track playtime.
import uuid  # To generate filenames for the Fourier transform cache.

import metadata  # To find or generate the Fourier transform image.
import music_control  # To control the currently playing track.
import preferences  # To get the playlist.
import storage  # To cache Fourier transform images.

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
		if len(current_playlist) == 0:  # Nothing left in the playlist.
			self.is_playing_set(False)
			return

		next_song = current_playlist[0]["path"]
		logging.info(f"Starting playback of track: {next_song}")
		Player.current_track = pygame.mixer.Sound(next_song)
		Player.control_track = music_control.MusicControl(next_song, Player.current_track, self)

		fourier_file = metadata.get(next_song, "fourier")
		if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
			fourier = self.generate_fourier(Player.current_track, next_song)
			filename = os.path.splitext(os.path.basename(next_song))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
			filepath = os.path.join(storage.cache(), "fourier", filename)
			fourier.save(filepath)
			metadata.change(next_song, "fourier", filepath)

		Player.start_time = time.time()
		Player.current_track.play()
		Player.control_track.play()

	def generate_fourier(self, sound, path):
		"""
		Generate an image of the fourier transform of a track.
		:param sound: A sound sample to generate the Fourier transform from.
		:param path: A path to the file we're generating the Fourier transform for.
		:return: A QImage of the Fourier transform of the given track.
		"""
		logging.debug(f"Generating Fourier image for {path}")
		# Get some metadata about this sound. We need the number of (stereo) channels and the bit depth.
		mutagen_file = mutagen.File(path)
		stereo_channels = mutagen_file.info.channels
		if hasattr(mutagen_file.info, "bits_per_sample"):
			bit_depth = mutagen_file.info.bits_per_sample
		else:  # Mutagen doesn't expose bit depth for MP3 files. Only bitrate (which is the compressed bit rate) and sample rate. They don't tell anything about what is in the waveform bytes.
			bit_depth = 16  # Assume 16-bit, which is common.
		waveform_dtype = numpy.byte if bit_depth == 8 else numpy.short

		# Get the waveform and transform it into frequency space.
		waveform = sound.get_raw()
		prefs = preferences.Preferences.getInstance()
		num_chunks = prefs.get("player/fourier_samples")
		num_channels = prefs.get("player/fourier_channels")
		waveform_numpy = numpy.frombuffer(waveform, dtype=waveform_dtype)[::stereo_channels]  # Only take one channel, e.g. the left stereo channel.
		chunks = numpy.array_split(waveform_numpy, num_chunks)  # Split the sound in chunks, each of which will be displayed as 1 horizontal pixel.
		chunk_size = len(chunks[0])
		split_points = numpy.logspace(1, math.log10(chunk_size), num_channels).astype(numpy.int32)  # We'll display a certain number of frequencies as vertical pixels. They are logarithmically spaced on the frequency spectrum.
		split_points = split_points[:-1]  # The last one is not a split point, but the end. No need to split there.

		transformed = numpy.zeros((num_chunks, num_channels), dtype=numpy.float)  # Result array for the transformed chunks.
		for i, chunk in enumerate(chunks):
			fourier = scipy.fft.rfft(chunk)
			fourier = numpy.abs(fourier[0:len(fourier) // 2])  # Ignore the top 50% of the image which repeats due to Nyquist.
			fourier_buckets = numpy.split(fourier, split_points)  # Split the frequencies into logarithmically-spaced ranges.
			fourier_pixels = numpy.array([numpy.sum(arr) for arr in fourier_buckets])  # Then sum up those ranges to get the brightness for individual pixels.
			transformed[i] = fourier_pixels
		# Normalise so that it fits in the 8-bit grayscale channel of the image.
		max_value = numpy.max(transformed)
		transformed /= max_value / 255
		normalised = transformed.astype(numpy.ubyte)

		# Generate an image from it.
		normalised = numpy.flip(numpy.transpose(normalised), axis=0).copy()  # Transposed to have time horizontally, frequency vertically. Flipped to have bass at the bottom, trebles at the top.
		result = PySide6.QtGui.QImage(normalised, num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)  # Reinterpret as pixels. Easy image!
		return result