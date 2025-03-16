import numpy as np
from scipy.fft import fft, fftfreq
from datetime import datetime

def fft_analysis(timestamps, data):
    N = len(data)
    start = timestamps[0]
    end = timestamps[-1]
    
    duration = (end - start).total_seconds()
    
    sample_rate = N / duration

    print(sample_rate)
    
    yf = fft(data)
    xf = fftfreq(N, d=1.0 / sample_rate)
    
    return xf[:N // 2].tolist(), (2.0 / N * np.abs(yf[:N // 2])).tolist()
