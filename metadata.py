# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import mutagen  # To read metadata from music files.
import mutagen.easyid3
import mutagen.flac
import mutagen.mp3
import mutagen.ogg
import mutagen.wave
import os.path  # To know where to store the database.
import sqlite3  # To cache metadata on disk.
import threading  # To restrict access to the database by one thread at a time.

import storage  # To know where to store the database.

def connect():
	"""
	Connect to the metadata database and return the connection.
	:return: A handle for the database containing metadata.
	"""
	db_file = os.path.join(storage.cache(), "metadata.db")
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
			cachetime real
		)""")
	else:
		connection = sqlite3.connect(db_file)

	return connection

database = {}  # Database connection created for each thread.
database_lock = threading.Lock()

def get_cached(path, field):
	"""
	Get a metadata field from the cache about a certain file.
	:param path: The file to get the metadata field from.
	:param field: The name of the metadata field to get. Must be a column of the metadata table!
	:return: The value cached for that field. Will be ``None`` if there is no cached information about that field.
	"""
	with database_lock:
		connection = database.get(threading.current_thread().ident, connect())
		cursor = connection.execute("SELECT ? FROM metadata WHERE path = ?", (field, path))
	if cursor.rowcount <= 0:
		return None  # No metadata at all about the specified file.
	with database_lock:
		row = cursor.fetchone()  # There should only be one row with that same path, since the primary key must be unique.
	return row[0]

def get_entry(path, field) -> str:
	"""
	Get a metadata entry from a certain file.

	If there is an entry in the cache and it is up-to-date, it will be obtained from that cache. Otherwise it will be
	read from the file itself.
	:param path: The file to get the metadata entry from.
	:param field: The name of the metadata field to get. Must be a column of the metadata table!
	:return: The value of that field. Returns an empty string if the metadata could not be read.
	"""
	with database_lock:
		connection = database.get(threading.current_thread().ident, connect())
		cursor = connection.execute(f"SELECT cachetime, {field} FROM metadata WHERE path = ?", (path, ))
		row = cursor.fetchone()

	if row is None:
		update_metadata(path)
		with database_lock:
			cursor = connection.execute(f"SELECT cachetime, {field} FROM metadata WHERE path = ?", (path, ))
			row = cursor.fetchone()
		if row is None:
			logging.warning(f"Unable to get metadata from file: {path}")
			return ""
	last_modified = os.path.getmtime(path)
	if last_modified > row[0]:
		update_metadata(path)
		with database_lock:
			cursor = connection.execute(f"SELECT cachetime, {field} FROM metadata WHERE path = ?", (path, ))
			row = cursor.fetchone()
		if row is None:
			logging.warning(f"Unable to update metadata from file: {path}")
			return ""
	return row[1]  # Return the requested field.

def update_metadata(path):
	"""
	Update all metadata fields of a certain file and store it in the cache.
	:param path: The file to read the metadata from.
	"""
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

	last_modified = os.path.getmtime(path)

	with database_lock:
		connection = database.get(threading.current_thread().ident, connect())
		connection.execute("INSERT OR REPLACE INTO metadata (path, title, author, comment, duration, bpm, cachetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
			(path, title, author, comment, duration, bpm, last_modified))
		connection.commit()