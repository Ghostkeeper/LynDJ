# Music player software aimed at Lindy Hop DJs.
# Copyright (C) 2023 Ghostkeeper
# This application is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this application. If not, see <https://gnu.org/licenses/>.

"""
A collection of functions that generate spectrograph images of music tracks.
"""

import logging
import math  # Transformation into log space for more human-oriented display in the result images.
import miniaudio  # To load waveforms of audio files.
import numpy  # For fast operations on waveform data.
import os.path  # To find and store Fourier images in the cache.
import PySide6.QtGui  # The resulting spectrograph images are stored in this format.
import scipy.fft  # To perform a Fourier transform of the waveform data.
import uuid  # To generate file names for Fourier images in the cache.

import lyndj.metadata  # To check if we already have Fourier images and to store where they are generated.
import lyndj.preferences  # To get parameters on how to generate Fourier images.
import lyndj.sound  # To store waveforms of audio tracks.
import lyndj.storage  # To find and store Fourier images in the cache.

def load_and_generate_fourier(path: str) -> None:
	"""
	Load a sound waveform and generate a Fourier image with it.

	This is less efficient than generating a Fourier image from an already loaded sound. The waveform is discarded
	afterwards.
	The resulting Fourier image is stored on disk, to be cached for later use.
	If there is already a Fourier image for this sound, it is not re-generated.
	:param path: The path to the file we're generating the Fourier transform for.
	"""
	logging.debug(f"Caching Fourier image for {path}")
	fourier_file = lyndj.metadata.get(path, "fourier")
	if fourier_file == "" or not os.path.exists(fourier_file):  # Not generated yet.
		decoded = miniaudio.decode_file(path)
		segment = lyndj.sound.Sound(decoded.samples.tobytes(), sample_size=decoded.sample_width, channels=decoded.nchannels, frame_rate=decoded.sample_rate)
		segment = segment.trim_silence()
		fourier = generate_fourier(segment, path)
		filename = os.path.splitext(os.path.basename(path))[0] + uuid.uuid4().hex[:8] + ".png"  # File's filename, but with an 8-character random string to prevent collisions.
		filepath = os.path.join(lyndj.storage.cache(), "fourier", filename)
		fourier.save(filepath)
		lyndj.metadata.change(path, "fourier", filepath)

def generate_fourier(sound: lyndj.sound.Sound, path: str) -> PySide6.QtGui.QImage:
	"""
	Generate an image of the Fourier transform of a track.
	:param sound: A sound sample to generate the Fourier transform from.
	:param path: A path to the file we're generating the Fourier transform for.
	:return: A QImage of the Fourier transform of the given track.
	"""
	logging.debug(f"Generating Fourier image for {path}")
	# Get some metadata about this sound. We need the number of (stereo) channels and the bit depth.
	sound = sound.to_mono()  # Mix to mono.

	# Get the waveform and transform it into frequency space.
	prefs = lyndj.preferences.Preferences.get_instance()
	num_chunks = prefs.get("player/fourier_samples")
	num_channels = prefs.get("player/fourier_channels")
	if len(sound.samples) == 0:  # We were unable to read the audio file.
		logging.error(f"Unable to read waveform from audio file to generate Fourier: {path}")
		return PySide6.QtGui.QImage(numpy.zeros((num_channels, num_chunks), dtype=numpy.ubyte), num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)

	waveform_dtype = numpy.byte if sound.sample_size == 1 else numpy.short if sound.sample_size == 2 else int
	waveform_numpy = numpy.frombuffer(sound.samples, dtype=waveform_dtype)
	chunks = numpy.array_split(waveform_numpy, num_chunks)  # Split the sound in chunks, each of which will be displayed as 1 horizontal pixel.
	chunk_size = len(chunks[0])
	split_points = numpy.logspace(1, math.log10(chunk_size), num_channels).astype(numpy.int32)  # We'll display a certain number of frequencies as vertical pixels. They are logarithmically spaced on the frequency spectrum.
	split_points = split_points[:-1]  # The last one is not a split point, but the end. No need to split there.

	transformed = numpy.zeros((num_chunks, num_channels), dtype=float)  # Result array for the transformed chunks.
	for i, chunk in enumerate(chunks):
		fourier = scipy.fft.rfft(chunk)
		fourier = numpy.abs(fourier[0:len(fourier) // 2])  # Ignore the top 50% of the image which repeats due to Nyquist.
		fourier_buckets = numpy.split(fourier, split_points)  # Split the frequencies into logarithmically-spaced ranges.
		fourier_pixels = numpy.array([numpy.sum(arr) for arr in fourier_buckets])  # Then sum up those ranges to get the brightness for individual pixels.
		transformed[i] = fourier_pixels
	# Normalise so that it fits in the 8-bit grayscale channel of the image.
	max_value = numpy.max(transformed)
	transformed /= max_value / 255
	transformed = numpy.power(255 * (transformed / 255), prefs.get("player/fourier_gamma"))  # Make the image a bit brighter (gamma correction factor 1.5).
	normalised = transformed.astype(numpy.ubyte)

	# Generate an image from it.
	normalised = numpy.flip(numpy.transpose(normalised), axis=0).copy()  # Transposed to have time horizontally, frequency vertically. Flipped to have bass at the bottom, trebles at the top.
	result = PySide6.QtGui.QImage(normalised, num_chunks, num_channels, PySide6.QtGui.QImage.Format_Grayscale8)  # Reinterpret as pixels. Easy image!
	return result