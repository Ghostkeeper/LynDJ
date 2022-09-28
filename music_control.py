# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import PySide6.QtCore  # For QTimers to execute code after a certain amount of time.

import metadata  # To get the events for a track.

class MusicControl:
	"""
	A music control track that sees to it when the music needs to stop, have its volume changed, trigger the next song
	to play, and so on.

	This object will generate a bunch of events to execute at certain timestamps in the track, and will start a bunch of
	timers for those events. It controls the pausing, resuming and cancelling of those events if playback is
	interrupted.
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

		# Create a list of events for this track.
		self.events = []
		duration = metadata.get(path, "duration")
		song_end_timer = PySide6.QtCore.QTimer()
		song_end_timer.setInterval(round(duration * 1000))
		song_end_timer.setSingleShot(True)
		self.events.append(song_end_timer)