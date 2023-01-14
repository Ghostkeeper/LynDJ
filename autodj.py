# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

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
		return ""  # TODO