# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import os  # To get OS-specific paths.
import os.path  # To construct new paths.
import platform  # To store things in a different location depending on the operating system.

def config() -> str:
	"""
	Get the location where configuration files should be stored.
	:return: A path to a directory where the configuration of the application is stored.
	"""
	system = platform.system()
	if system == "Windows":
		try:
			path = os.environ["APPDATA"]
		except KeyError:
			path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
	else:  # Linux or unknown.
		try:
			path = os.environ["XDG_CONFIG_HOME"]  # XDG standard storage location.
		except KeyError:
			path = os.path.join(os.path.expanduser("~"), ".config")  # Most Linux machines.
	return os.path.join(path, "lyndj")

def cache() -> str:
	"""
	Get the location where cache files should be stored.
	:return: A path to a directory where the cache of the application is stored.
	"""
	system = platform.system()
	if system == "Windows":
		try:
			path = os.environ["APPDATA"]
		except KeyError:
			path = os.path.join(os.path.expanduser("~"), "AppData", "Local")
	else:  # Linux or unknown.
		try:
			path = os.environ["XDG_CACHE_HOME"]  # XDG standard storage location.
		except KeyError:
			path = os.path.join(os.path.expanduser("~"), ".cache")  # Most Linux machines.
	return os.path.join(path, "lyndj")

def data() -> str:
	"""
	Get the location where data files should be stored.
	:return: A path to a directory where data for the application is stored.
	"""
	system = platform.system()
	if system == "Windows":
		try:
			path = os.environ["LOCALAPPDATA"]
		except KeyError:
			path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
	else:  # Linux or unknown.
		try:
			path = os.environ["XDG_DATA_HOME"]  # XDG standard storage location.
		except KeyError:
			path = os.path.join(os.path.expanduser("~"), ".local", "share")  # Most Linux machines.
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
	fourier_path = os.path.join(cache(), "fourier")
	if not os.path.exists(fourier_path):
		logging.debug(f"Creating fourier subfolder in {fourier_path}")
		os.makedirs(fourier_path)
	data_path = data()
	if not os.path.exists(data_path):
		logging.info(f"Creating data directory in {data_path}")
		os.makedirs(data_path)

def source() -> str:
	"""
	Get the location of the source code or installation folder.
	:return: A path to the directory where the application is installed.
	"""
	return os.getcwd()  # lyndj.py sets the CWD to its directory at start-up.