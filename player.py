# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import pygame  # The media player we're using to play music.
import PySide6.QtCore  # Exposing the player to QML.

class Player(PySide6.QtCore.QObject):
	"""
	An object that is responsible for playing music files, controlling how they're played (pause, play, volume,
	equaliser, etc.) and exporting information on what is playing (track and progress).

	This object only has class methods. All of the state is static and global, to prevent collisions with the underlying
	media APIs. The only reason it is an object is to expose the methods to QML easily so that they can be controlled
	from there.
	"""

	sounds = {}  # Dict mapping paths to sound files to pre-loaded sound objects in Pygame.

	def preload(self, path) -> None:
		"""
		Load an audio file into memory, readying it for playback without latency.

		This function is best called on a thread that does not block the interface. It will not hold the GIL though.
		:param path: A path to an audio file to load for playback.
		"""
		if path in self.sounds:
			return  # Already pre-loaded.
		self.sounds[path] = pygame.mixer.Sound(path)