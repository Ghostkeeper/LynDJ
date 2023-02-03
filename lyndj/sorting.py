# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

"""
Some sorting utility functions.
"""

class ReverseOrder:
	"""
	Causes the comparison between instances to be inverted.
	"""
	def __init__(self, instance):
		"""
		Wraps the reverse order around the given object.
		:param instance: The object to invert comparisons of.
		"""
		self.instance = instance

	def __eq__(self, other):
		"""
		Tests if this object is equal to the other.
		:param other: Another object to test equality to.
		:return: ``True`` if the two objects are equal, or ``False`` if they are not.
		"""
		if type(other) == ReverseOrder:
			return self.instance == other.instance
		return self.instance == other

	def __lt__(self, other):
		"""
		Tests if this object should be sorted before the other.

		However, it is considered that this object would be sorted before the other if it is greater. This ordering is
		inverted, which is the main purpose of this class.
		:param other: Another object to compare to.
		:return: ``True`` if this object should be sorted before the other object, or ``False`` if it should be sorted
		after.
		"""
		if type(other) == ReverseOrder:
			return self.instance > other.instance  # Inverted comparison!
		return self.instance > other