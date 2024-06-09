# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2024 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

"""
A collection of functions to actually play audio on the system.
"""
import numpy  # To export Sound objects to a playback buffer.
import pyaudio  # Used to play audio.
import time  # To sleep the thread when there is no audio to play.
import threading  # The audio is played on a different thread.
import typing

import lyndj.player  # To get the playback parameters.
import lyndj.preferences

if typing.TYPE_CHECKING:
	import lyndj.sound

audio_source: typing.Optional["lyndj.sound.Sound"] = None
"""
The audio track that is currently being played.
"""

current_position = 0.0
"""
The location in the file where we are currently playing (in seconds).
"""

end_position = 0.0
"""
The location in the file where the song ends (in seconds).
"""

def play(new_audio: "lyndj.sound.Sound") -> None:
	"""
	Start the playback of a new audio source.
	:param new_audio: The new audio source to play.
	"""
	global audio_source
	audio_source = new_audio

def stop() -> None:
	"""
	Stop playing any audio.
	"""
	global audio_source
	audio_source = None
	global current_position
	current_position = 0.0

def swap(new_audio: "lyndj.sound.Sound") -> None:
	"""
	Swap out an audio source for another without changing the playback position.
	:param new_audio: The new audio source to play.
	"""
	global audio_source
	audio_source = new_audio

def filter(chunk: "lyndj.sound.Sound") -> "lyndj.sound.Sound":
	"""
	Apply effects to a chunk of audio.

	This will be called on each chunk individually, which is a short interval of audio, so it should perform well.

	The filters applied currently are:
	- Volume.
	- Conversion to mono.
	:param chunk: A chunk of audio.
	:return: A filtered chunk of audio.
	"""
	# Apply player volume.
	volume = lyndj.player.Player.main_volume
	chunk = chunk * volume

	# Convert to mono, if necessary.
	if lyndj.player.Player.is_mono:
		chunk = chunk.to_mono()

	return chunk

def play_loop() -> None:
	"""
	Main loop of the playback server.

	This function runs indefinitely. It should be ran on a different thread than the main GUI thread.
	It will continuously look for the current position in the current audio source and play it, applying filters if
	necessary.
	"""
	global current_position
	global audio_source
	audio_server = None
	stream = None

	try:
		audio_server = pyaudio.PyAudio()
		current_sample_width = 0
		current_channels = 0
		current_rate = 0
		while True:
			if audio_source is None:
				time.sleep(0.1)  # Sleep until we have an audio source.
				continue
			chunk_size = lyndj.preferences.Preferences.get_instance().get("player/buffer_size") / 1000.0
			chunk = audio_source[current_position:current_position + chunk_size]
			chunk = filter(chunk)
			if chunk.channels[0].itemsize != current_sample_width or chunk.frame_rate != current_rate or len(chunk.channels) != current_channels:
				# New audio source, so re-generate the stream.
				if stream:
					stream.stop_stream()
					stream.close()
				current_sample_width = chunk.channels[0].itemsize
				current_rate = chunk.frame_rate
				current_channels = len(chunk.channels)
				stream = audio_server.open(format=audio_server.get_format_from_width(current_sample_width), rate=current_rate, channels=current_channels, output=True)
			if current_position >= end_position:  # Playback completed. Stop taking the GIL and go into stand-by.
				current_position = 0
				audio_source = None
				continue
			samples = numpy.empty(chunk.channels[0].size * len(chunk.channels), dtype=chunk.channels[0].dtype)
			for channel_num, channel in enumerate(chunk.channels):
				samples[channel_num::len(chunk.channels)] = channel
			stream.write(samples.tobytes())
			current_position += chunk_size
	finally:
		if stream:
			stream.stop_stream()
			stream.close()
		if audio_server:
			audio_server.terminate()

play_thread = threading.Thread(target=play_loop, daemon=True)
"""
A thread that continuously sends audio to the system to play.
"""
play_thread.start()  # Start that thread to feed audio to the system.