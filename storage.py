# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os  # To get OS-specific paths.
import os.path  # To construct new paths.

def config() -> str:
	"""
	Get the location where configuration files should be stored.
	:return: A path to a directory where the configuration of the application is stored.
	"""
	try:
		path = os.environ["XDG_CONFIG_HOME"]  # XDG standard storage location.
	except KeyError:
		path = os.path.expanduser("~/.config")  # Most Linux machines.
	return os.path.join(path, "lyndj")

def cache() -> str:
	"""
	Get the location where cache files should be stored.
	:return: A path to a directory where the cache of the application is stored.
	"""
	try:
		path = os.environ["XDG_CACHE_HOME"]  # XDG standard storage location.
	except KeyError:
		path = os.path.expanduser("~/.cache")  # Most Linux machines.
	return os.path.join(path, "lyndj")

def ensure_exists() -> None:
	"""
	Ensure that the storage locations all exist.
	"""
	config_path = config()
	if not os.path.exists(config_path):
		logging.info(f"Creating configuration directory in {config_path}")
		os.makedirs(config_path)
	cache_path = cache()
	if not os.path.exists(cache_path):
		logging.info(f"Creating cache directory in {cache_path}")
		os.makedirs(cache_path)