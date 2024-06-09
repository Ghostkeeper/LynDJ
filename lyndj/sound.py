# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2024 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

import logging
import math  # To calculate audio RMS.
import numpy  # For fast operations on wave data.
import typing

class Sound:
	"""
	This class represents an audio segment.

	It contains the raw audio data (samples), as well as some metadata on how to interpret it, such as frame rate.
	"""

	@classmethod
	def from_mono(cls, left: "Sound", right: "Sound") -> "Sound":
		"""
		Combine two mono sounds into one stereo sound.
		:param left: The left audio channel.
		:param right: The right audio channel.
		:return: A combined stereo channel.
		"""
		assert len(left.channels) == 1
		assert len(right.channels) == 1
		assert left.frame_rate == right.frame_rate
		assert len(left.channels[0]) == len(right.channels[0])

		return Sound([left.channels[0], right.channels[0]], frame_rate=left.frame_rate)

	def __init__(self, channels: list[numpy.array], frame_rate: int=44100) -> None:
		"""
		Construct a new audio clip using the raw sample data.
		:param channels: Audio signal waveforms. This is a list of arrays, one array of audio data for each channel.
		Each array enumerates the audio samples for that channel. The data type of these waveforms can vary depending on
		the bit depth of the audio signal, but should always be integer-based.
		:param frame_rate: The number of frames to play per second (Hz).
		"""
		self.channels = channels
		self.frame_rate = frame_rate

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
		start = round(start * self.frame_rate)
		end = round(end * self.frame_rate)
		clipped = [channel[start:end] for channel in self.channels]
		return Sound(clipped, self.frame_rate)

	def duration(self) -> float:
		"""
		Get the length of the sound, in seconds.
		:return: How long it takes to play this sound.
		"""
		return len(self.channels[0]) / self.frame_rate

	def rms(self) -> float:
		"""
		Get the Root Mean Square level of this sound.

		This is a measure of roughly how loud the signal is.
		:return: The RMS of this sound, in values (not dB, but between 0 and the maximum possible sample value).
		"""
		sum_squares = 0
		num_samples = 0
		for channel in self.channels:
			sum_squares += channel.square().sum()
			num_samples += len(channel)
		return int(math.sqrt(sum_squares / num_samples))

	def detect_silence(self, threshold: float=-64.0) -> typing.Tuple[float, float]:
		"""
		Find silence at the start and end of the track.
		:param threshold: Audio amplitude below this threshold is considered silence. In decibels.
		:return: A tuple containing two timestamps: One near the start of the track, one near the end. Both timestamps
		are relative to the start of the track.
		"""
		max_value = (2 ** (self.channels[0].dtype.itemsize * 8 - 1))
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

		logging.debug(f"Silence is {round(start_trim, 2)}s from the start, {round(self.duration() - end_trim, 2)}s from the end of the track.")
		return start_trim, end_trim

	def trim_silence(self, threshold: float=-64.0) -> "Sound":
		"""
		Remove parts of silence from the start and end of this sound.
		:param threshold: Audio amplitude below this threshold is considered silence. In decibels.
		:return: A trimmed sound object.
		"""
		start_trim, end_trim = self.detect_silence(threshold)
		return self[start_trim:end_trim]

	def to_mono(self) -> "Sound":
		"""
		Mix this sound to mono.
		:return: A new sound with only one channel, where the audio has been mixed to mono.
		"""
		if len(self.channels) == 1:  # Already mono.
			return self

		mixed_channels = numpy.zeros((len(self.channels[0]), ))
		for channel in self.channels:
			mixed_channels += channel
		mixed_channels = (mixed_channels / len(self.channels)).astype(self.channels[0].dtype)
		return Sound([mixed_channels], frame_rate=self.frame_rate)

	def __mul__(self, volume: float) -> "Sound":
		"""
		Amplify the sound.
		:param volume: A volume factor.
		:return: A new sound, with the amplitude multiplied by the given volume factor.
		"""
		new_channels = [(channel * volume).astype(channel.dtype) for channel in self.channels]
		return Sound(new_channels, frame_rate=self.frame_rate)