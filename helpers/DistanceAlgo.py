# ===========================================================================
# Copyright (C) 2021-2022 Infineon Technologies AG
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===========================================================================

import numpy as np
from scipy import signal, constants


from helpers.fft_spectrum import *


class DistanceAlgo:
    """Algorithm for computation of distance FFT from raw data"""

    def __init__(self, num_samples,end_frequency_Hz,start_frequency_Hz, num_chirps_per_frame: int):
        self.num_chirps_per_frame = num_chirps_per_frame

        # compute Blackman-Harris Window matrix over chirp samples(range)
        self.range_window = signal.blackmanharris(num_samples).reshape(1, num_samples)

        bandwidth_hz = abs(end_frequency_Hz - start_frequency_Hz)
        fft_size = num_samples * 2
        self.range_bin_length = constants.c / (2 * bandwidth_hz * fft_size / num_samples)
        self.skip = 10

    def compute_distance(self, chirp_data):
        # Computes distance using chirp data
        # chirp_data: single antenna chirp data

        # Step 1 - calculate range fft spectrum of the frame
        range_fft = fft_spectrum(chirp_data, self.range_window)

        # Step 2 - convert to absolute spectrum
        range_fft_abs = abs(range_fft)

        # Step 3 - coherent integration of all chirps
        distance_data = np.divide(range_fft_abs.sum(axis=0), self.num_chirps_per_frame)
        #distance_data  = np.fft.fftshift(distance_data)
        
        # Step 4 - peak search and distance calculation
    
        distance_peak = np.argmax(distance_data[self.skip:])

        distance_peak_m = self.range_bin_length * (distance_peak + self.skip)
        return distance_peak_m, distance_data,self.range_bin_length,self.skip
