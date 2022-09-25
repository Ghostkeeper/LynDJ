# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

class MusicControl:
	"""
	A music control track that sees to it when the music needs to stop, have its volume changed, trigger the next song
	to play, and so on.

	This will run a separate thread that continuously watches the time played on the currently playing song. At certain
	timestamps, it will trigger events.
	"""

	def __init__(self, path, sound, player):
		"""
		Creates a music control track for a certain song.
		:param path: The path to the file that this track is controlling the music for.
		:param sound: The Pygame sound that this track is controlling.
		:param player: The player to control the sound with.
		"""
		self.path = path
		self.sound = sound
		self.player = player

	def loop(self):
		"""
		This function will be called multiple times per second in order to allow this track to exert control over the
		music.

		The performance of this function is quite critical. Anything happening in this loop needs to be able to execute
		at the frequency that the loop is called. Occasionally triggering a more expensive function is okay, as long as
		this doesn't happen during playback of the actual song.
		"""
		pass  # TODO