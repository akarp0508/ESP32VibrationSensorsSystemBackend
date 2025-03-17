import numpy as np
from scipy.fft import fft, fftfreq
from datetime import datetime

def fft_analysis(timestamps, data):
    N = len(data)
    if(N==0):
        return list(),list()
    start = timestamps[0]
    end = timestamps[-1]
    
    duration = (end - start).total_seconds()
    
    sample_rate = N / duration

    print(sample_rate)
    
    yf = fft(data)
    xf = fftfreq(N, d=1.0 / sample_rate)
    
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