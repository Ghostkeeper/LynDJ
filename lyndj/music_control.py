# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import PySide6.QtCore  # For QTimers to execute code after a certain amount of time.
import typing

import lyndj.metadata  # To get the events for a track.
import lyndj.playback  # To stop audio playback when stopping playing.
import lyndj.playlist  # To remove the track from the playlist when it finishes playing.
import lyndj.preferences  # For some playback preferences.
import lyndj.waypoints_timeline  # To parse waypoints.

if typing.TYPE_CHECKING:
	import lyndj.sound
	import lyndj.player

class MusicControl:
	"""
	A music control track that sees to it when the music needs to stop, have its volume changed, trigger the next song
	to play, and so on.

	This object will generate a bunch of events to execute at certain timestamps in the track, and will start a bunch of
	timers for those events. It controls the pausing, resuming and cancelling of those events if playback is
	interrupted.
	"""

	def __init__(self, path: str, sound: "lyndj.sound.Sound", player: "lyndj.player.Player") -> None:
		"""
		Creates a music control track for a certain song.
		:param path: The path to the file that this track is controlling the music for.
		:param sound: The sound segment that this track is controlling.
		:param player: The player to control the sound with.
		"""
		self.path = path
		self.sound = sound
		self.player = player

		pause_between_songs = lyndj.preferences.Preferences.get_instance().get("player/silence") * 1000

		# Create a list of events for this track.
		self.events: typing.List[PySide6.QtCore.QTimer] = []

		# Song ends.
		duration = sound.duration()
		song_end_timer = PySide6.QtCore.QTimer()
		song_end_timer.setInterval(round(duration * 1000 + pause_between_songs))
		song_end_timer.setSingleShot(True)
		song_end_timer.timeout.connect(self.song_ends)
		self.events.append(song_end_timer)

		# Volume transitions.
		volume_waypoints = lyndj.metadata.get(path, "volume_waypoints")
		volume_waypoints = lyndj.waypoints_timeline.WaypointsTimeline.parse_waypoints(volume_waypoints)
		if len(volume_waypoints) > 0:
			volume = 0.5
			pos = -1
			t = 0.025
			while t < duration:
				if t >= volume_waypoints[pos + 1][0]:
					pos += 1
					if pos >= len(volume_waypoints) - 1:
						break  # After last waypoint.
				if pos < 0:
					t += 0.05
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
				t += 0.05

	def play(self) -> None:
		"""
		Start all the timers for the events, causing the events to occur in order.
		"""
		for event in self.events:
			event.start()

	def stop(self) -> None:
		"""
		Cancel all of the timers for the events, interrupting them from being executed.
		"""
		for event in self.events:
			event.stop()

	def fadeout(self, duration: float) -> None:
		"""
		Fade out the music playback.
		:param duration: How slowly to fade out to zero volume.
		"""
		self.stop()  # Stop all normal events first.
		self.events = []
		time = 0.1
		start_volume = self.player.volume
		while time < duration:
			new_volume = (1 - (time / duration)) * start_volume
			timer = PySide6.QtCore.QTimer()
			timer.setInterval(round(time * 1000))
			timer.setSingleShot(True)
			timer.timeout.connect(lambda v=new_volume: self.player.set_volume(v))
			timer.setTimerType(PySide6.QtCore.Qt.PreciseTimer)
			self.events.append(timer)
			time += 0.05  # Adjust volume every 0.05s.
		# And another event for the final 0 volume.
		def fadeout_done():
			self.player.set_volume(0)
			lyndj.player.Player.current_track = None
			lyndj.player.Player.control_track = None
			lyndj.playback.stop()
		timer = PySide6.QtCore.QTimer()
		timer.setInterval(round(duration * 1000))
		timer.setSingleShot(True)
		timer.timeout.connect(lambda: fadeout_done())
		timer.setTimerType(PySide6.QtCore.Qt.PreciseTimer)
		self.events.append(timer)
		for event in self.events:
			event.start()

	def song_ends(self) -> None:
		"""
		Triggered when the music file has finished playing.
		"""
		logging.debug(f"Event for {self.path}: Song ends")
		# Remove the previous track from the playlist.
		self.player.song_finished.emit(self.path)
		lyndj.playlist.Playlist.get_instance().remove(0)
		self.player.play_next()