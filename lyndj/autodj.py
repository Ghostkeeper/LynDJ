# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2024 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import collections  # Using defaultdict.
import logging
import os  # To find the candidate tracks.
import os.path  # To find the candidate tracks.
import time  # To find tracks that were played this session (within 24 hours ago).
import typing

import lyndj.history  # To decide on new tracks to play based on recently played tracks.
import lyndj.metadata  # To decide on the next track to play by their metadata.
import lyndj.preferences  # To get the current playlist and music directory.

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

	energy_to_numeric: typing.Dict[str, int] = {
		"low": 0,
		"medium": 50,
		"high": 100
	}
	"""
	Convert the energy level in track metadata to a numeric value, between 0 and 100.
	"""

	def suggested_track(self) -> str:
		"""
		Get the currently suggested track to append to the playlist.

		This is the track that the automatic DJ would suggest adding next.
		:return: The next track to add to the playlist.
		"""
		prefs = lyndj.preferences.Preferences.get_instance()
		if not prefs.has("directory/browse_path"):
			return ""
		directory = prefs.get("directory/browse_path")
		candidates = set(filter(lyndj.metadata.is_music_file, [os.path.join(directory, filename) for filename in os.listdir(directory)]))

		# Don't suggest excluded files.
		candidates = {path for path in candidates if lyndj.metadata.has(path) and lyndj.metadata.get(path, "autodj_exclude") == 0}

		candidates -= set(prefs.get("playlist/playlist"))  # Anything in the playlist is not allowed to be in there twice.
		if len(candidates) == 0:
			return ""  # No candidates left to add to the playlist.

		# For age, style and energy, we want variation in the playlist. Get the frequencies of each value in recent history (weighted).
		history = self.get_history()
		age_histogram = collections.defaultdict(float)
		style_histogram = collections.defaultdict(float)
		energy_histogram = collections.defaultdict(float)
		for i, path in enumerate(history):
			age = lyndj.metadata.get(path, "age")
			style = lyndj.metadata.get(path, "style")
			energy = lyndj.metadata.get(path, "energy")
			weight = 1.0 / (i + 1.0)
			if age != "":
				age_histogram[age] += weight
			if style != "":
				style_histogram[style] += weight
			if energy != "":
				energy_histogram[energy] += weight
		# If the age/style/energy is unknown, make it average.
		age_histogram[""] = sum(age_histogram.values()) / len(age_histogram) if age_histogram else 0
		style_histogram[""] = sum(style_histogram.values()) / len(style_histogram) if style_histogram else 0
		energy_histogram[""] = sum(energy_histogram.values()) / len(energy_histogram) if energy_histogram else 0

		# See where in the BPM cadence we are currently.
		autodj_bpm_cadence = [int(item) for item in prefs.get("autodj/bpm_cadence").strip(",").split(",")]
		history_to_match = reversed(history[:len(autodj_bpm_cadence)])
		bpm_to_match = [lyndj.metadata.get(path, "bpm") for path in history_to_match]
		bpm_to_match = [bpm if bpm >= 0 else prefs.get("playlist/medium_bpm") for bpm in bpm_to_match]  # If BPM is unknown, use medium BPM.
		best_rotate = -1
		best_rotate_difference = float("inf")
		for rotate_n in range(len(autodj_bpm_cadence)):
			rotated_bpm_cadence = autodj_bpm_cadence[rotate_n:] + autodj_bpm_cadence[:rotate_n]
			bpm_difference = 0  # Let's sum the differences between the BPM of the tracks and the cadence.
			for i, bpm in enumerate(bpm_to_match):
				bpm_difference += abs(rotated_bpm_cadence[i] - bpm)
			if bpm_difference < best_rotate_difference:
				best_rotate = rotate_n
				best_rotate_difference = bpm_difference
		bpm_target = autodj_bpm_cadence[(len(bpm_to_match) + best_rotate) % len(autodj_bpm_cadence)]
		autodj_energy = prefs.get("autodj/energy")
		bpm_target += (autodj_energy - 50) * prefs.get("autodj/energy_slider_power")

		autodj_age_variation = prefs.get("autodj/age_variation")
		autodj_style_variation = prefs.get("autodj/style_variation")
		autodj_energy_variation = prefs.get("autodj/energy_variation")
		autodj_bpm_precision = prefs.get("autodj/bpm_precision")
		autodj_slider_power = prefs.get("autodj/energy_slider_power")
		autodj_last_played_influence = prefs.get("autodj/last_played_influence")
		best_rating = float("-inf")
		best_track = ""
		for path in sorted(candidates):
			rating = 0

			# Penalties for age, style and energy that have recently been played often.
			age = lyndj.metadata.get(path, "age")
			style = lyndj.metadata.get(path, "style")
			energy = lyndj.metadata.get(path, "energy")
			try:
				numeric_energy = self.energy_to_numeric[energy.lower()]
			except KeyError:
				numeric_energy = 50  # Default.

			age_penalty = age_histogram[age]
			style_penalty = style_histogram[style]
			energy_penalty = energy_histogram[energy]
			numeric_energy_penalty = abs(numeric_energy - autodj_energy)
			rating -= autodj_age_variation * age_penalty
			rating -= autodj_style_variation * style_penalty
			rating -= autodj_energy_variation * energy_penalty
			rating -= 0.2 * autodj_slider_power * numeric_energy_penalty

			# Bonus for tracks that are played long ago.
			if autodj_last_played_influence > 0:
				long_ago = time.time() - lyndj.metadata.get(path, "last_played")
				long_ago /= 3600 * 24 * 7 * autodj_last_played_influence
				rating += long_ago

			# Penalties for tracks that are far from the target BPM.
			rating -= abs(lyndj.metadata.get(path, "bpm") - bpm_target) * autodj_bpm_precision

			if rating > best_rating:
				best_track = path
				best_rating = rating

		logging.debug(f"The AutoDJ suggests track: {best_track}")
		return best_track

	def get_history(self) -> typing.List[str]:
		"""
		Get a list of tracks, in order of when they were last played.

		This history of tracks includes the history of tracks that would've been played before the suggested track, i.e.
		all of the tracks of the playlist.

		The most recently played track will be returned first in the list. Only tracks that were played in the current
		session will be returned.
		:return: The tracks that were played in the current session, in order of when they were played.
		"""
		history = [track["path"] for track in lyndj.history.History.get_instance().track_data]
		playlist = lyndj.preferences.Preferences.get_instance().get("playlist/playlist")
		result = list(reversed(playlist)) + history
		result = filter(lambda track: not track.startswith(":"), result)
		return list(result)