# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import array  # For fast operations on wave data.
import logging
import math  # To calculate audio RMS.
import typing

class Sound:
	"""
	This class represents an audio segment.

	It contains the raw audio data (samples), as well as some metadata on how to interpret it, such as frame rate,
	number of channels and sample size.
	"""

	@classmethod
	def from_mono(cls, left: "Sound", right: "Sound") -> "Sound":
		"""
		Combine two mono sounds into one stereo sound.
		:param left: The left audio channel.
		:param right: The right audio channel.
		:return: A combined stereo channel.
		"""
		assert left.channels == 1
		assert right.channels == 1
		assert left.frame_rate == right.frame_rate
		assert left.sample_size == right.sample_size
		assert len(left.samples) == len(right.samples)

		new_data = bytes(len(left.samples) * 2)
		new_data[0::2] = left.samples
		new_data[1::2] = right.samples
		return Sound(new_data, frame_rate=left.frame_rate, channels=2, sample_size=left.sample_size)

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

	def rms(self) -> float:
		"""
		Get the Root Mean Square level of this sound.

		This is a measure of roughly how loud the signal is.
		:return: The RMS of this sound, in values (not dB, but between 0 and the maximum possible sample value).
		"""
		num_samples = len(self.samples) / self.sample_size
		if num_samples == 0:
			return 0.0
		size_to_array_type = {
			1: "b",
			2: "H",
			4: "I"
		}
		sample_array = array.array(size_to_array_type[self.sample_size])
		sample_array.frombytes(self.samples)
		sum_squares = sum(sample ** 2 for sample in sample_array)
		return int(math.sqrt(sum_squares / num_samples))

	def trim_silence(self, threshold: float=-64.0) -> "Sound":
		"""
		Remove parts of silence from the start and end of this sound.
		:param threshold: Audio amplitude below this threshold is considered silence. In decibels.
		:return: A trimmed sound object.
		"""
		max_value = (2 ** (self.sample_size * 8 - 1))
		threshold_value = 10 ** (threshold / 20) * max_value
		slice_size = 0.01  # Break the audio in 10ms slices, to check each slice for its volume.

		# Forward scan from the start.
		start_trim = 0
		while start_trim < self.duration():
			slice = self[start_trim:start_trim + slice_size]
			if slice.rms() > threshold_value:
				break
			start_trim += slice_size
		# Backward scan from the end.
		end_trim = self.duration() - slice_size
		while end_trim > 0:
			slice = self[end_trim:end_trim + slice_size]
			if slice.rms() > threshold_value:
				break
			end_trim -= slice_size

		logging.debug(f"Trimmed {start_trim}s from the start, {self.duration() - end_trim}s of silence from the end of the track.")
		return self[start_trim:end_trim]

	def to_mono(self) -> "Sound":
		"""
		Mix this sound to mono.
		:return: A new sound with only one channel, where the audio has been mixed to mono.
		"""
		if self.channels == 1:  # Already mono.
			return self

		size_to_array_type = {
			1: "b",
			2: "H",
			4: "I"
		}
		sample_array = array.array(size_to_array_type[self.sample_size])
		sample_array.frombytes(self.samples)
		mixed_array = array.array(size_to_array_type[self.sample_size])
		for i in range(len(sample_array) // self.channels):
			mixed_array[i] = sum((sample_array[i * self.channels + j] for j in range(self.channels))) / self.channels
		mixed_data = mixed_array.tobytes()
		return Sound(mixed_data, frame_rate=self.frame_rate, channels=1, sample_size=self.sample_size)

	def __mul__(self, volume: float) -> "Sound":
		"""
		Amplify the sound.
		:param volume: A volume factor.
		:return: A new sound, with the amplitude multiplied by the given volume factor.
		"""
		size_to_array_type = {
			1: "b",
			2: "H",
			4: "I"
		}
		sample_array = array.array(size_to_array_type[self.sample_size])
		sample_array.frombytes(self.samples)
		for i in range(len(sample_array)):
			sample_array[i] *= volume
		return Sound(sample_array.tobytes(), frame_rate=self.frame_rate, channels=self.channels, sample_size=self.sample_size)