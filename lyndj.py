# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2022 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import signal  # To catch interrupts that need to stop the application.
import sys  # Return correct exit code.

import application

"""
Entry point for the application. This starts a QtApplication.
"""

if __name__ == "__main__":
	# Set logging to our preferences.
	logging.basicConfig(format="%(levelname)s:%(asctime)s | %(message)s", level=logging.INFO)

	signal.signal(signal.SIGINT, signal.SIG_DFL)  # Python is not handling SIGINT, so let the kernel do that.
	app = application.Application(sys.argv)
	sys.exit(app.exec())