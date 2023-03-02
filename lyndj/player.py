# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import math  # Transformations on the Fourier transform.
import miniaudio  # To decode audio files.
import numpy  # For the Fourier transform in Scipy.
import os.path  # To cache Fourier transform images.
import PySide6.QtCore  # Exposing the player to QML.
import PySide6.QtGui  # For the QImage to display the Fourier transform.
import scipy.fft  # For the Fourier transform.
import time  # To track playtime.
import typing
import uuid  # To generate filenames for the Fourier transform cache.

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

		decoded = miniaudio.decode_file(next_song)
		track = lyndj.sound.Sound(decoded.samples.tobytes(), sample_size=decoded.sample_width, channels=decoded.nchannels, frame_rate=decoded.sample_rate)
		Player.current_track = track.trim_silence()
		Player.control_track = lyndj.music_control.MusicControl(next_song, Player.current_track, self)

		fourier_file = lyndj.metadata.get(next_song, "fourier")
		if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
			fourier = self.generate_fourier(Player.current_track, next_song)
			filename = os.path.splitext(os.path.basename(next_song))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
			filepath = os.path.join(lyndj.storage.cache(), "fourier", filename)
			fourier.save(filepath)
			lyndj.metadata.change(next_song, "fourier", filepath)

		self.set_volume(0.5)  # Back to default for the next song.

		self.song_changed.emit()  # We loaded up a new song.
		Player.start_time = time.time()
		lyndj.playback.play(Player.current_track)
		Player.control_track.play()

	def load_and_generate_fourier(self, path: str) -> None:
		"""
		Load a sound waveform and generate a Fourier image with it.

		This is less efficient than generating a Fourier image from an already loaded sound. The waveform is discarded
		afterwards.
		The resulting Fourier image is stored on disk, to be cached for later use.
		If there is already a Fourier image for this sound, it is not re-generated.
		:param path: The path to the file we're generating the Fourier transform for.
		"""
		logging.debug(f"Caching Fourier image for {path}")
		fourier_file = lyndj.metadata.get(path, "fourier")
		if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
			decoded = miniaudio.decode_file(path)
			segment = lyndj.sound.Sound(decoded.samples.tobytes(), sample_size=decoded.sample_width, channels=decoded.nchannels, frame_rate=decoded.sample_rate)
			segment = segment.trim_silence()
			fourier = self.generate_fourier(segment, path)
			filename = os.path.splitext(os.path.basename(path))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
			filepath = os.path.join(lyndj.storage.cache(), "fourier", filename)
			fourier.save(filepath)
			lyndj.metadata.change(path, "fourier", filepath)

	def generate_fourier(self, sound: lyndj.sound.Sound, path: str) -> PySide6.QtGui.QImage:
		"""
		Generate an image of the Fourier transform of a track.
		:param sound: A sound sample to generate the Fourier transform from.
		:param path: A path to the file we're generating the Fourier transform for.
		:return: A QImage of the Fourier transform of the given track.
		"""
		logging.debug(f"Generating Fourier image for {path}")
		# Get some metadata about this sound. We need the number of (stereo) channels and the bit depth.
		sound = sound.to_mono()  # Mix to mono.

		# Get the waveform and transform it into frequency space.
		prefs = lyndj.preferences.Preferences.get_instance()
		num_chunks = prefs.get("player/fourier_samples")
		num_channels = prefs.get("player/fourier_channels")
		if len(sound.samples) == 0:  # We were unable to read the audio file.
			logging.error(f"Unable to read waveform from audio file to generate Fourier: {path}")
			return PySide6.QtGui.QImage(numpy.zeros((num_channels, num_chunks), dtype=numpy.ubyte), num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)

		waveform_dtype = numpy.byte if sound.sample_size == 1 else numpy.short if sound.sample_size == 2 else int
		waveform_numpy = numpy.frombuffer(sound.samples, dtype=waveform_dtype)
		chunks = numpy.array_split(waveform_numpy, num_chunks)  # Split the sound in chunks, each of which will be displayed as 1 horizontal pixel.
		chunk_size = len(chunks[0])
		split_points = numpy.logspace(1, math.log10(chunk_size), num_channels).astype(numpy.int32)  # We'll display a certain number of frequencies as vertical pixels. They are logarithmically spaced on the frequency spectrum.
		split_points = split_points[:-1]  # The last one is not a split point, but the end. No need to split there.

		transformed = numpy.zeros((num_chunks, num_channels), dtype=float)  # Result array for the transformed chunks.
		for i, chunk in enumerate(chunks):
			fourier = scipy.fft.rfft(chunk)
			fourier = numpy.abs(fourier[0:len(fourier) // 2])  # Ignore the top 50% of the image which repeats due to Nyquist.
			fourier_buckets = numpy.split(fourier, split_points)  # Split the frequencies into logarithmically-spaced ranges.
			fourier_pixels = numpy.array([numpy.sum(arr) for arr in fourier_buckets])  # Then sum up those ranges to get the brightness for individual pixels.
			transformed[i] = fourier_pixels
		# Normalise so that it fits in the 8-bit grayscale channel of the image.
		max_value = numpy.max(transformed)
		transformed /= max_value / 255
		transformed = numpy.power(255 * (transformed / 255), prefs.get("player/fourier_gamma"))  # Make the image a bit brighter (gamma correction factor 1.5).
		normalised = transformed.astype(numpy.ubyte)

		# Generate an image from it.
		normalised = numpy.flip(numpy.transpose(normalised), axis=0).copy()  # Transposed to have time horizontally, frequency vertically. Flipped to have bass at the bottom, trebles at the top.
		result = PySide6.QtGui.QImage(normalised, num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)  # Reinterpret as pixels. Easy image!
		return result

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
		current_path = current_playlist[0]
		fourier_path = lyndj.metadata.get(current_path, "fourier")
		return PySide6.QtCore.QUrl.fromLocalFile(fourier_path)

	@PySide6.QtCore.Property(float, notify=song_changed)
	def current_duration(self) -> float:
		"""
		Get the duration of the current song, in seconds.

		If there is no current song playing, this returns 0.
		:return: The duration of the current song, in seconds.
		"""
		if Player.current_track is None:
			return 0
		return Player.current_track.duration()

	@PySide6.QtCore.Property(str, notify=song_changed)
	def current_title(self) -> str:
		"""
		Get the title of the current song.
		:return: The title of the currently playing song.
		"""
		current_playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		if len(current_playlist) == 0:
			return ""
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