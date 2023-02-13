# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import pyaudio  # Used to play audio.
import pydub.utils  # For volume effects.
import time  # To sleep the thread when there is no audio to play.
import threading  # The audio is played on a different thread.

import lyndj.player  # To get the playback parameters.
import lyndj.preferences

audio_source = None
current_position = 0  # Location in the file where we are currently playing (in ms).

def play(new_audio):
	"""
	Start the playback of a new audio source.
	:param new_audio: The new audio source to play.
	"""
	global audio_source
	audio_source = new_audio
	global current_position
	current_position = 0  # Start from the start.

def swap(new_audio):
	"""
	Swap out an audio source for another without changing the playback position.
	:param new_audio: The new audio source to play.
	"""
	global audio_source
	audio_source = new_audio

def filter(chunk):
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
	gain = pydub.utils.ratio_to_db(volume)
	chunk = chunk + gain

	# Convert to mono, if necessary.
	if lyndj.player.Player.is_mono and chunk.channels == 2:
		channels = chunk.split_to_mono()
		new = channels[0].overlay(channels[1]) - 4  # -4dB because we're doubling the sound, so we must halve the amplitude first.
		chunk = pydub.AudioSegment.from_mono_audiosegments(new, new)

	return chunk

def play_loop():
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
			if audio_source.sample_width != current_sample_width or audio_source.frame_rate != current_rate or audio_source.channels != current_channels:
				# New audio source, so re-generate the stream.
				if stream:
					stream.stop_stream()
					stream.close()
				current_sample_width = audio_source.sample_width
				current_rate = audio_source.frame_rate
				current_channels = audio_source.channels
				stream = audio_server.open(format=audio_server.get_format_from_width(current_sample_width), rate=current_rate, channels=current_channels, output=True)
			if current_position >= len(audio_source):  # Playback completed. Stop taking the GIL and go into stand-by.
				audio_source = None
				continue
			chunk_size = lyndj.preferences.Preferences.get_instance().get("player/buffer_size")
			chunk = audio_source[current_position:current_position + chunk_size]
			chunk = filter(chunk)
			stream.write(chunk.raw_data)
			current_position += chunk_size
	finally:
		if stream:
			stream.stop_stream()
			stream.close()
		if audio_server:
			audio_server.terminate()

play_thread = threading.Thread(target=play_loop, daemon=True)
play_thread.start()