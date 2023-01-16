# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import collections  # Using defaultdict.
import os  # To find the candidate tracks.
import os.path  # To find the candidate tracks.
import time  # To find tracks that were played this session (within 24 hours ago).

import metadata  # To decide on the next track to play by their metadata.
import preferences  # To get the current playlist and music directory.

class AutoDJ:
	"""
	This class suggests the next track to play based on recently played tracks.

	The next track to play will get added to the playlist automatically with a marker to indicate that it is a track
	that was suggested by the auto DJ. This track can then be accepted by the user. User-added tracks will take
	precedence over any tracks that haven't been accepted yet. If the playlist is empty, automatically suggested tracks
	will start playing automatically until the end of the session.

	The suggestion for the best track to play depends on:
	* The music directory, to select tracks from.
	* The track's BPM, to have a regular cadence of fast and slow tracks.
	* The age and style of the track, to maximise variation in the playlist.
	* When it was last played, to prioritise tracks that are rarely played.
	* The energy level and BPM of the track, to match audience energy levels as configured by the user.
	"""

	def suggested_track(self) -> str:
		"""
		Get the currently suggested track to append to the playlist.

		This is the track that the automatic DJ would suggest adding next.
		:return: The next track to add to the playlist.
		"""
		prefs = preferences.Preferences.getInstance()
		directory = prefs.get("browse_path")
		candidates = set(filter(metadata.is_music_file, [os.path.join(directory, filename) for filename in os.listdir(directory)]))

		candidates -= set(prefs.get("playlist/playlist"))  # Anything in the playlist is not allowed to be in there twice.
		if len(candidates) == 0:
			return ""  # No candidates left to add to the playlist.

		# For age and style, we want variation in the playlist. Get the frequencies of each value in recent history (weighted).
		history = self.get_history()
		age_histogram = collections.defaultdict(float)
		style_histogram = collections.defaultdict(float)
		for i, path in enumerate(history):
			age = metadata.get(path, "age")
			style = metadata.get(path, "style")
			weight = 1.0 / (i + 1.0)
			if age != "":
				age_histogram[age] += weight
			if style != "":
				style_histogram[style] += weight

		

	def get_history(self) -> list:
		"""
		Get a list of tracks, in order of when they were last played.

		This history of tracks includes the history of tracks that would've been played before the suggested track, i.e.
		all of the tracks of the playlist.

		The most recently played track will be returned first in the list. Only tracks that were played in the current
		session (within the last 24 hours) will be returned.
		:return: The tracks that were played in the current session, in order of when they were played.
		"""
		prefs = preferences.Preferences.getInstance()
		directory = prefs.get("browse_path")
		paths = set(filter(metadata.is_music_file, [os.path.join(directory, filename) for filename in os.listdir(directory)]))
		playlist = prefs.get("playlist/playlist")
		paths -= set(playlist)  # The playlist will be the files that are most recently played by the time the suggested track plays. Add them later.
		one_day_ago = time.time() - 20 * 24 * 3600
		paths = [path for path in paths if metadata.get(path, "last_played") >= one_day_ago]  # Only include tracks that were played this session, i.e. today.
		paths = list(sorted(paths, key=lambda path: metadata.get(path, "last_played"), reverse=True))
		return list(reversed(playlist)) + paths