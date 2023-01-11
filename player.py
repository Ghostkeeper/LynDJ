# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import math  # Transformations on the Fourier transform.
import numpy  # For the Fourier transform in Scipy.
import os.path  # To cache Fourier transform images.
import pydub  # The media player we're using to play music.
import pydub.utils  # For our custom silence detector.
import pydub.playback  # The playback module of Pydub.
import PySide6.QtCore  # Exposing the player to QML.
import PySide6.QtGui  # For the QImage to display the Fourier transform.
import scipy.fft  # For the Fourier transform.
import time  # To track playtime, and last played time.
import uuid  # To generate filenames for the Fourier transform cache.

import metadata  # To find or generate the Fourier transform image.
import music_control  # To control the currently playing track.
import playback  # To actually play the music.
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

	instance = None
	"""
	This class is a singleton. This stores the one instance that is allowed to exist.
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
	def get_instance(cls):
		"""
		Get the single instance of this class, or create it if it wasn't created yet.
		:return: The instance of this class.
		"""
		if cls.instance is None:
			cls.instance = Player()
		return cls.instance

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
		if not prefs.has("player/silence"):
			prefs.add("player/silence", 2.0)  # 2 seconds silence between songs by default.
		if not prefs.has("player/mono"):
			prefs.add("player/mono", False)  # Whether to play audio in mono or not.

		Player.is_mono = prefs.get("player/mono")

	def is_playing_set(self, new_is_playing) -> None:
		"""
		Start or stop the music.
		:param new_is_playing: Whether the music should be playing or not.
		"""
		if Player.current_track is None and new_is_playing:
			self.play_next()
		elif Player.current_track is not None and not new_is_playing:
			logging.info(f"Stopping playback.")
			fading = Player.current_track.fade(to_gain=-120, start=playback.current_position, duration=round(preferences.Preferences.getInstance().get("player/fadeout") * 1000))
			playback.swap(fading)
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
		if next_song.endswith(".flac"):
			codec = "flac"
		else:
			codec = None
		track = pydub.AudioSegment.from_file(next_song, codec=codec)
		Player.current_track = self.trim_silence(track)
		Player.control_track = music_control.MusicControl(next_song, Player.current_track, self)

		fourier_file = metadata.get(next_song, "fourier")
		if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
			fourier = self.generate_fourier(Player.current_track, next_song)
			filename = os.path.splitext(os.path.basename(next_song))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
			filepath = os.path.join(storage.cache(), "fourier", filename)
			fourier.save(filepath)
			metadata.change(next_song, "fourier", filepath)

		self.set_volume(0.5)  # Back to default for the next song.

		self.songChanged.emit()  # We loaded up a new song.
		Player.start_time = time.time()
		playback.play(Player.current_track)
		Player.control_track.play()

		metadata.change(next_song, "last_played", time.time())

	def trim_silence(self, track):
		"""
		Trims silence from the start and end of a track.
		:param track: A track to trim.
		:return: A trimmed track.
		"""
		threshold_db = -64  # If the volume gets below -64db, we consider it silence.
		threshold_value = pydub.utils.db_to_float(threshold_db) * track.max_possible_amplitude
		slice_size = 10  # Break the audio in 10ms slices, to check each slice for its volume.

		# Forward scan from the start.
		pos = 0
		for pos in range(0, len(track), slice_size):
			slice = track[pos:pos + slice_size]
			if slice.rms > threshold_value:
				break
		start_trim = pos

		# Backward scan from the end.
		pos = len(track) - slice_size
		for pos in range(len(track) - slice_size, 0, -slice_size):
			slice = track[pos:pos + slice_size]
			if slice.rms > threshold_value:
				break
		end_trim = pos + slice_size

		return track[start_trim:end_trim]

	def load_and_generate_fourier(self, path):
		"""
		Load a sound waveform and generate a Fourier image with it.

		This is less efficient than generating a Fourier image from an already loaded sound. The waveform is discarded
		afterwards.
		The resulting Fourier image is stored on disk, to be cached for later use.
		If there is already a Fourier image for this sound, it is not re-generated.
		:param path: The path to the file we're generating the Fourier transform for.
		"""
		logging.debug(f"Caching Fourier image for {path}")
		fourier_file = metadata.get(path, "fourier")
		if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
			segment = pydub.AudioSegment.from_file(path)
			segment = self.trim_silence(segment)
			fourier = self.generate_fourier(segment, path)
			filename = os.path.splitext(os.path.basename(path))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
			filepath = os.path.join(storage.cache(), "fourier", filename)
			fourier.save(filepath)
			metadata.change(path, "fourier", filepath)

	def generate_fourier(self, sound, path):
		"""
		Generate an image of the Fourier transform of a track.
		:param sound: A sound sample to generate the Fourier transform from.
		:param path: A path to the file we're generating the Fourier transform for.
		:return: A QImage of the Fourier transform of the given track.
		"""
		logging.debug(f"Generating Fourier image for {path}")
		# Get some metadata about this sound. We need the number of (stereo) channels and the bit depth.
		sound = sound.set_channels(1)  # Mix to mono.
		bit_depth = sound.sample_width * 8
		waveform_dtype = numpy.byte if bit_depth == 8 else numpy.short if bit_depth == 16 else numpy.int

		# Get the waveform and transform it into frequency space.
		waveform = sound.get_array_of_samples()
		num_samples = math.floor(len(waveform) / sound.sample_width)
		waveform = waveform[:num_samples * sound.sample_width]
		prefs = preferences.Preferences.getInstance()
		num_chunks = prefs.get("player/fourier_samples")
		num_channels = prefs.get("player/fourier_channels")
		if len(waveform) == 0:  # We were unable to read the audio file.
			logging.error(f"Unable to read waveform from audio file to generate Fourier: {path}")
			return PySide6.QtGui.QImage(numpy.zeros((num_channels, num_chunks), dtype=numpy.ubyte), num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)

		waveform_numpy = numpy.frombuffer(waveform, dtype=waveform_dtype)
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
		transformed = numpy.power(255 * (transformed / 255), 1.5)  # Make the image a bit brighter (gamma correction factor 1.5).
		normalised = transformed.astype(numpy.ubyte)

		# Generate an image from it.
		normalised = numpy.flip(numpy.transpose(normalised), axis=0).copy()  # Transposed to have time horizontally, frequency vertically. Flipped to have bass at the bottom, trebles at the top.
		result = PySide6.QtGui.QImage(normalised, num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)  # Reinterpret as pixels. Easy image!
		return result

	songChanged = PySide6.QtCore.Signal()

	@PySide6.QtCore.Property(str, notify=songChanged)
	def currentFourier(self) -> str:
		"""
		Get the path to the currently playing song's Fourier image.
		:return: A path to an image.
		"""
		current_playlist = preferences.Preferences.getInstance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return ""
		current_path = current_playlist[0]["path"]
		return metadata.get(current_path, "fourier")

	@PySide6.QtCore.Property(float, notify=songChanged)
	def currentDuration(self) -> float:
		"""
		Get the duration of the current song, in seconds.

		If there is no current song playing, this returns 0.
		:return: The duration of the current song, in seconds.
		"""
		if Player.current_track is None:
			return 0
		return len(Player.current_track) / 1000.0

	@PySide6.QtCore.Property(str, notify=songChanged)
	def currentTitle(self) -> str:
		"""
		Get the title of the current song.
		:return: The title of the currently playing song.
		"""
		current_playlist = preferences.Preferences.getInstance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return ""
		current_path = current_playlist[0]["path"]  # Don't request from the playlist, which may be outdated. Get directly from metadata.
		return metadata.get(current_path, "title")

	@PySide6.QtCore.Property(str, notify=songChanged)
	def currentPath(self) -> str:
		"""
		Get the path to the current song.
		:return: The path of the currently playing song.
		"""
		current_playlist = preferences.Preferences.getInstance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return ""
		return current_playlist[0]["path"]

	volume_changed = PySide6.QtCore.Signal()
	"""
	Triggered when something changes the playback volume of the current song.
	"""

	def set_volume(self, value) -> None:
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

	def set_mono(self, value) -> None:
		"""
		Changes the mono toggle.
		:param value: The new value, whether to play mono (True) or stereo (False).
		"""
		if Player.is_mono != value:
			Player.is_mono = value
			preferences.Preferences.getInstance().set("player/mono", value)
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