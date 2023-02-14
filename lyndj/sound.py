# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import typing

class Sound:
	"""
	This class represents an audio segment.

	It contains the raw audio data (samples), as well as some metadata on how to interpret it, such as frame rate,
	number of channels and sample size.
	"""

	def __init__(self, samples: bytes, frame_rate: int=44100, channels: int=2, sample_size: int=2) -> None:
		"""
		Construct a new audio sample using the raw sample data.
		:param samples: Raw sample data of the audio waveforms. This data enumerates each of the frames in a row. Each
		frame enumerates the samples for each channel in a row. Each sample is ``sample_size`` bytes.
		:param frame_rate: The number of frames to play per second (Hz).
		:param channels: The number of audio channels to play. For instance, 2 channels is stereo sound.
		:param sample_size: The size of each sample in each channel in each frame, in bytes. For instance, a sample size
		of 2 represents 16-bit audio.
		"""
		# If the bytes is not divisible by integer number of frames, cut off the end.
		bytes_per_frame = sample_size * channels
		extraneous_bytes = len(samples) % bytes_per_frame
		if extraneous_bytes > 0:
			samples = samples[:-extraneous_bytes]

		self.samples = samples
		self.frame_rate = frame_rate
		self.channels = channels
		self.sample_size = sample_size

	def __getitem__(self, index: typing.Union[int, float, slice]) -> "Sound":
		"""
		Gets a sub-segment of this sound.

		If the segment given is partly out of range, the sound will be shorter than the desired length.

		The step element of a slice is ignored. Only the start and the end of the slice is used.

		The index and slice bounds are given by the duration in the song, in seconds. They can be ``float``s.
		:param index: Either a single number to indicate a timestamp that you want to access, or a slice to indicate a
		range of time.
		:return: A part of this sound. If given a single index, the sound will last for at most 1 second. If given a
		range, the sound will be the length of that range.
		"""
		duration = self.duration()
		start = 0.0
		end = duration
		if isinstance(index, slice):
			if index.start:
				start = index.start
			if index.stop:
				end = index.stop
		else:
			start = index
			end = (index + 1)

		# Negative indices indicate a duration from the end of the sound.
		if start < 0:
			start += duration
		if end < 0:
			end += duration
		# Clamp to the range of duration of the sound.
		start = max(0.0, min(duration, start))
		end = max(0.0, min(duration, end))
		# Convert to positions in the sample array.
		start = round(start * self.sample_size * self.channels * self.frame_rate)
		end = round(end * self.sample_size * self.channels * self.frame_rate)
		return Sound(self.samples[start:end], self.frame_rate, self.channels, self.sample_size)

	def duration(self) -> float:
		"""
		Get the length of the sound, in seconds.
		:return: How long it takes to play this sound.
		"""
		return len(self.samples) / self.sample_size / self.channels / self.frame_rate