# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import pyaudio  # Used to play audio.
import time  # To sleep the thread when there is no audio to play.
import threading  # The audio is played on a different thread.

audio_source = None
chunk_size = 100  # Size of chunks to send to audio server, in ms. Larger chunks are more efficient, but cause greater delays.
current_position = 0  # Location in the file where we are currently playing (in ms).

def play(new_audio):
	global audio_source
	audio_source = new_audio
	global current_position
	current_position = 0

def play_loop():
	global current_position
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
			stream.write(audio_source[current_position:current_position + chunk_size]._data)
			current_position += chunk_size
	finally:
		if stream:
			stream.stop_stream()
			stream.close()
		if audio_server:
			audio_server.terminate()

play_thread = threading.Thread(target=play_loop, daemon=True)
play_thread.start()