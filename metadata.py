# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import mutagen  # To read metadata from music files.
import mutagen.easyid3
import mutagen.flac
import mutagen.id3
import mutagen.mp3
import mutagen.ogg
import mutagen.wave
import os.path  # To know where to store the database.
import PySide6.QtCore  # For a timer to write the database.
import sqlite3  # To cache metadata on disk.

import storage  # To know where to store the database.

metadata = {}
"""
The single source of truth for the currently known metadata.

To quickly access metadata for certain files, look into this dictionary. The keys of the dictionary are absolute paths
to music files. The values are dictionaries of metadata key-values.
"""

def load():
	"""
	Reads the metadata from the database file into memory.

	All of the metadata in the database file will get stored in the ``metadata`` dict.
	"""
	db_file = os.path.join(storage.data(), "metadata.db")
	if not os.path.exists(db_file):
		return  # No metadata to read.
	connection = sqlite3.connect(db_file)
	logging.debug("Reading metadata from database.")

	new_metadata = {}  # First store it in a local variable (faster). Merge afterwards.
	for path, title, author, comment, duration, bpm, last_played, fourier, cachetime in connection.execute("SELECT * FROM metadata"):
		new_metadata[path] = {
			"path": path,
			"title": title,
			"author": author,
			"comment": comment,
			"duration": duration,
			"bpm": bpm,
			"last_played": last_played,
			"fourier": fourier,
			"cachetime": cachetime
		}
	metadata.update(new_metadata)

def store():
	"""
	Serialises the metadata on disk in a database file.
	"""
	db_file = os.path.join(storage.data(), "metadata.db")
	if not os.path.exists(db_file):
		# Create the database anew.
		logging.info("Creating metadata database.")
		connection = sqlite3.connect(db_file)
		connection.execute("""CREATE TABLE metadata(
			path text PRIMARY KEY,
			title text,
			author text,
			comment text,
			duration real,
			bpm real,
			last_played real,
			fourier text,
			cachetime real
		)""")
	else:
		connection = sqlite3.connect(db_file)

	local_metadata = metadata  # Cache locally for performance.
	for path, entry in local_metadata.items():
		connection.execute("INSERT OR REPLACE INTO metadata (path, title, author, comment, duration, bpm, last_played, fourier, cachetime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(path, entry["title"], entry["author"], entry["comment"], entry["duration"], entry["bpm"], entry["last_played"], entry["fourier"], entry["cachetime"]))
	connection.commit()

# When we change the database, save the database to disk after a short delay.
# If there's multiple changes in short succession, those will be combined into a single write.
store_timer = PySide6.QtCore.QTimer()
store_timer.setSingleShot(True)
store_timer.setInterval(250)
store_timer.timeout.connect(store)

def get(path, field):
	"""
	Get a metadata field from the cache about a certain file.
	:param path: The file to get the metadata field from.
	:param field: The name of the metadata field to get. Must be one of the known metadata fields in the database!
	:return: The value of the metadata entry for that field. Will be ``None`` if there is no cached information about
	that field.
	"""
	return metadata[path][field]

def add(path, entry):
	"""
	Add or override a metadata entry for a certain file.
	:param path: The path to the file that the metadata is for.
	:param entry: A dictionary containing metadata.
	"""
	metadata[path] = entry
	store_timer.start()

def add_file(path):
	"""
	Read the metadata from a given file and store it in our database.

	This will check if the file has been modified since it was last stored in the database. If the database is still up
	to date, nothing is changed. If the entry is not present in the database or outdated, it will add or update the
	entry respectively.
	:param path: The path to the file to read the metadata from.
	"""
	local_metadata = metadata  # Cache locally for performance.
	last_modified = os.path.getmtime(path)
	if path in local_metadata:
		if local_metadata[path]["cachetime"] >= last_modified:
			return  # Already up to date.
		last_played = local_metadata[path]["last_played"]
	else:
		last_played = -1  # Never played.
	logging.debug(f"Updating metadata for {path}")

	try:
		f = mutagen.File(path)
		if type(f) in {mutagen.mp3.MP3, mutagen.wave.WAVE}:  # Uses ID3 tags.
			id3 = mutagen.easyid3.EasyID3(path)
			title = id3.get("title", [os.path.splitext(os.path.basename(path))[0]])[0]
			author = id3.get("artist", [""])[0]
			comment = f.get("COMM:ID3v1 Comment:eng", [""])[0]  # There is no EasyID3 for comments.
			bpm = id3.get("bpm", "-1")[0]
		elif isinstance(f, mutagen.ogg.OggFileType) or type(f) == mutagen.flac.FLAC:  # These types use Vorbis Comments.
			title = f.get("title", [os.path.splitext(os.path.basename(path))[0]])[0]
			author = f.get("artist", [""])[0]
			comment = f.get("comment", [""])[0]
			bpm = f.get("bpm", ["-1"])[0]
		else:  # Unknown file type.
			title = os.path.splitext(os.path.basename(path))[0]
			author = ""
			comment = ""
			bpm = -1
		duration = f.info.length
	except mutagen.MutagenError as e:
		logging.warning(f"Unable to get metadata from {path}: {e}")
		title = os.path.splitext(os.path.basename(path))[0]  # Take the file name without extension.
		author = ""
		comment = ""
		bpm = -1
		duration = -1

	try:
		bpm = float(bpm)
	except ValueError:
		bpm = -1

	add(path, {
		"path": path,
		"title": title,
		"author": author,
		"comment": comment,
		"duration": duration,
		"bpm": bpm,
		"last_played": last_played,
		"fourier": "",
		"cachetime": last_modified
	})

def change(path, key, value) -> None:
	"""
	Change an individual metadata element of a file, and change it also inside of that file.

	This changes the metadata inside of the metadata tags of the music file, if applicable.
	:param path: The path to the file to change metadata of.
	:param key: The metadata entry to change.
	:param value: The new value for this metadata entry.
	"""
	logging.info(f"Changing metadata of {path}: {key}={value}")

	# Some metadata will also be stored in the file.
	if key in {"title", "author", "comment", "bpm"}:
		try:
			f = mutagen.File(path)
			if type(f) in {mutagen.mp3.MP3, mutagen.wave.WAVE}:  # Uses ID3 tags.
				if key == "comment":  # There is no EasyID3 for comments.
					id3 = mutagen.id3.ID3(path)
					id3.setall("COMM:ID3v1 Comment:eng", [mutagen.id3.COMM(encoding=3, lang="eng", text=[value])])
					id3.save()
				else:
					if key == "author":
						save_key = "artist"
					else:
						save_key = key
					id3 = mutagen.easyid3.EasyID3(path)
					id3[save_key] = value
					id3.save()
			elif isinstance(f, mutagen.ogg.OggFileType) or type(f) == mutagen.flac.FLAC:  # These types use Vorbis Comments.
				if key == "author":
					save_key = "artist"
				else:
					save_key = key
				flac = mutagen.flac.FLAC(path)
				flac[save_key] = [value]
				flac.save()
			else:  # Unknown file type.
				logging.warning(f"Cannot save metadata to file type of {path}!")
		except mutagen.MutagenError as e:
			logging.error(f"Unable to save metadata in {path}: {e}")
			return

	metadata[path][key] = value
	store_timer.start()

def is_music_file(path) -> bool:
	"""
	Returns whether the given file is a music file that we can read.
	:param path: The file to check.
	:return: ``True`` if it is a music track, or ``False`` if it isn't.
	"""
	if not os.path.isfile(path):
		return False  # Only read files.
	ext = os.path.splitext(path)[1]
	return ext in [".mp3", ".flac", ".opus", ".ogg", ".wav"]  # Supported file formats.

def add_directory(path):
	"""
	Read the metadata from all music files in a directory (not its subdirectories) and store them in our database.

	This will update all metadata in the database about the files in this directory so that it's all up to date again.
	:param path: The path to the directory to read the files from.
	"""
	files = set(filter(is_music_file, [os.path.join(path, filename) for filename in os.listdir(path)]))
	for filepath in files:
		add_file(filepath)