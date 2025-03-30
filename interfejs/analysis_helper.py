import numpy as np
from scipy.fft import fft, fftfreq
from datetime import datetime

from scipy.interpolate import interp1d
from scipy.signal import detrend

def fft_analysis(timestamps, data):
    if len(data) == 0:
        return list(), list()

    timestamps = np.array([(t - timestamps[0]).total_seconds() for t in timestamps])
    data = np.array(data)

    total_duration = timestamps[-1] - timestamps[0]
    estimated_sample_rate = len(data) / total_duration

    uniform_timestamps = np.linspace(0, total_duration, len(data))

    interp_func = interp1d(timestamps, data, kind="linear", fill_value="extrapolate")
    uniform_data = interp_func(uniform_timestamps)

    uniform_data = detrend(uniform_data)

    N = len(uniform_data)
    yf = fft(uniform_data)
    xf = np.fft.fftfreq(N, d=1.0 / estimated_sample_rate)

    return xf[:N // 2].tolist(), (2.0 / N * np.abs(yf[:N // 2])).tolist()

def basic_analysis(data):
    if len(data) == 0:
        return "-", "-", "-", "-", "-", "-"
    
    # Perform basic analysis
    rms_value = np.sqrt(np.mean(np.square(data)))
    mean_value = np.mean(data)
    max_value = np.max(data)
    min_value = np.min(data)
    peak_to_peak_value = np.ptp(data)
    std_value = np.std(data)
    
    # Return values as formatted strings
    rms_str = f"{rms_value:.2f}"
    mean_str = f"{mean_value:.2f}"
    max_str = f"{max_value:.2f}"
    min_str = f"{min_value:.2f}"
    peak_to_peak_str = f"{peak_to_peak_value:.2f}"
    std_str = f"{std_value:.2f}"
    
    return rms_str, mean_str, max_str, min_str, peak_to_peak_str, std_str