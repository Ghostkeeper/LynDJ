# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import PySide6.QtCore  # Exposing this object to QML to see its progress.
import queue  # A task queue.
import threading  # To run tasks in a background thread.
import time  # To sleep the background thread regularly.

class BackgroundTasks(PySide6.QtCore.QObject):
	"""
	A runner that runs computation tasks in the background.

	These tasks will run periodically on a background thread, and are meant to not interrupt the user's interaction with
	the program.

	Some tasks can be ran whenever. Some tasks are only allowed to be started while the music is not playing.
	"""

	instance = None
	"""
	This class is a singleton. This stores the one instance that is allowed to exist.
	"""

	@classmethod
	def get_instance(cls):
		"""
		Get the single instance of this class, or create it if it wasn't created yet.
		:return: The instance of this class.
		"""
		if cls.instance is None:
			cls.instance = BackgroundTasks()
		return cls.instance

	def __init__(self, parent=None):
		"""
		Construct the task runner.

		This also starts a thread that waits for tasks to complete.
		:param parent: A parent QObject that this element is running under.
		"""
		super().__init__(parent)
		self.runner_thread = threading.Thread(target=self.worker, daemon=True)
		self.tasks = queue.SimpleQueue()  # A list of callables containing tasks to execute.
		self.num_done = 0  # How many tasks were completed since the queue was last empty. This is used to show a progress bar.
		self.runner_thread.start()

	def add(self, task):
		"""
		Add a task to be executed in the background.
		:param task: A callable object, which executes the task to be done in the background.
		"""
		self.tasks.put(task)
		self.progressChanged.emit()

	def worker(self):
		"""
		Continuously checks if there are background tasks to be done, and if so, does those tasks.

		This function never returns. It should be ran on a background daemon thread.
		"""
		while True:
			time.sleep(1)  # 1 second gives reasonably low priority to checking if there are any tasks to run.
			try:
				task = self.tasks.get(block=False)
			except queue.Empty:
				continue  # Just check again 1 iteration later.
			task()  # Execute this task.
			self.num_done += 1
			if self.tasks.empty():
				self.num_done = 0
			self.progressChanged.emit()  # Tell the front-end to update its progress trackers.

	progressChanged = PySide6.QtCore.Signal()
	"""
	If this signal fires, a progress tracker needs to be updated.
	"""

	@PySide6.QtCore.Property(float, notify=progressChanged)
	def progress(self):
		"""
		Get the current process as a fraction between 0 and 1.

		If the task queue is empty, this will return 1, to indicate that all work is done.
		If the task queue is not empty, it will show the progress towards completing all tasks obtained since the queue
		was last empty. For instance, if a single task is given the progress will report 0 at first. If another task is
		added before the first task completes, and then the first task completes, the progress is reported as 0.5.
		:return: A number between 0 and 1, indicating the progress of executing tasks in the queue.
		"""
		if self.tasks.empty():
			return 1.0
		return self.num_done / (self.num_done + self.tasks.qsize())