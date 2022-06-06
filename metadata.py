# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os.path  # To know where to store the database.
import sqlite3  # To cache metadata on disk.

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
			duration real,
			bpm real,
			cachetime datetime 
		)""")
	else:
		connection = sqlite3.connect(db_file)

	return connection

database = connect()

def get_cached(path, field):
	"""
	Get a metadata field from the cache about a certain file.
	:param path: The file to get the metadata field from.
	:param field: The name of the metadata field to get. Must be a column of the metadata table!
	:return: The value cached for that field. Will be ``None`` if there is no cached information about that field.
	"""
	cursor = database.execute("SELECT ? FROM metadata WHERE path = ?", (field, path))
	if cursor.rowcount <= 0:
		return None  # No metadata at all about the specified file.
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
	cursor = database.execute("SELECT cachetime, ? FROM metadata WHERE path = ?", (field, path))
	if cursor.rowcount <= 0:
		update_metadata(path)
		cursor = database.execute("SELECT cachetime, ? FROM metadata WHERE path = ?", (field, path))
		if cursor.rowcount <= 0:
			logging.warning(f"Unable to get metadata from file: {path}")
			return ""
	row = cursor.fetchone()
	last_modified = os.path.getmtime(path)
	if last_modified > row[0]:
		update_metadata(path)
		cursor = database.execute("SELECT cachetime, ? FROM metadata WHERE path = ?", (field, path))
		if cursor.rowcount <= 0:
			logging.warning(f"Unable to update metadata from file: {path}")
		else:
			row = cursor.fetchone()
	return row[1]  # Return the requested field.

def update_metadata(path):
	"""
	Update all metadata fields of a certain file and store it in the cache.
	:param path: The file to read the metadata from.
	"""
	pass  # TODO.