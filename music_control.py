# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import PySide6.QtCore  # For QTimers to execute code after a certain amount of time.

import metadata  # To get the events for a track.
import playlist  # To remove the track from the playlist when it finishes playing.
import player  # To change volume from events.
import preferences  # For some playback preferences.
import waypoints_timeline  # To parse waypoints.

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
		:param sound: The sound segment that this track is controlling.
		:param player: The player to control the sound with.
		"""
		self.path = path
		self.sound = sound
		self.player = player

		prefs = preferences.Preferences.getInstance()
		if not prefs.has("player/silence"):
			prefs.add("player/silence", 2.0)  # The pause between songs.
		pause_between_songs = prefs.get("player/silence") * 1000

		# Create a list of events for this track.
		self.events = []

		# Song ends.
		duration = len(sound)
		song_end_timer = PySide6.QtCore.QTimer()
		song_end_timer.setInterval(round(duration + pause_between_songs))
		song_end_timer.setSingleShot(True)
		song_end_timer.timeout.connect(self.song_ends)
		self.events.append(song_end_timer)

		# Volume transitions.
		volume_waypoints = metadata.get(path, "volume_waypoints")
		volume_waypoints = waypoints_timeline.WaypointsTimeline.parse_waypoints(volume_waypoints)
		if len(volume_waypoints) > 0:
			volume = 0.5
			pos = -1
			for t in range(25, duration, 50):  # Adjust volume every 50ms if applicable.
				t /= 1000.0  # Convert to seconds, to compare with timestamps from waypoints.
				if t >= volume_waypoints[pos + 1][0]:
					pos += 1
					if pos >= len(volume_waypoints) - 1:
						break  # After last waypoint.
				if pos < 0:
					continue  # Before first waypoint.
				# Interpolate the new volume.
				time_start, level_start = volume_waypoints[pos]
				time_end, level_end = volume_waypoints[pos + 1]
				if level_start == level_end:
					new_volume = level_start  # Common case: Flat between transitions.
				else:
					ratio = (t - time_start) / (time_end - time_start)
					new_volume = level_start + ratio * (level_end - level_start)
				if new_volume != volume:
					volume_change_timer = PySide6.QtCore.QTimer()
					volume_change_timer.setInterval(round(t * 1000))
					volume_change_timer.setSingleShot(True)
					volume_change_timer.timeout.connect(lambda v=new_volume: player.set_volume(v))
					volume_change_timer.setTimerType(PySide6.QtCore.Qt.PreciseTimer)
					self.events.append(volume_change_timer)
					volume = new_volume

	def play(self):
		"""
		Start all the timers for the events, causing the events to occur in order.
		"""
		for event in self.events:
			event.start()

	def stop(self):
		"""
		Cancel all of the timers for the events, interrupting them from being executed.
		"""
		for event in self.events:
			event.stop()

	def song_ends(self):
		"""
		Triggered when the music file has finished playing.
		"""
		logging.debug(f"Event for {self.path}: Song ends")
		# Remove the previous track from the playlist.
		playlist.Playlist.getInstance().remove(0)
		self.player.play_next()