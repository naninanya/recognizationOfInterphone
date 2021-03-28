import time
import pyaudio
import numpy as np
from scipy.signal import argrelmax

CHUNK = 1024
RATE = 8000

dt = 1/RATE
freq = np.linspace(0, 1.0/dt, CHUNK)
fn = 1/dt/2

FIRST_FREQ = 587
SECOND_FREQ = 740
THIRD_FREQ = 880
FREQ_ERR = 0.02

detect_first = False
detect_second = False
detect_third = False

# FFTで振幅最大の周波数を取得する関数


def getMaxFreqFFT(sound, chunk, freq):
    # FFT
    f = np.fft.fft(sound)/(chunk/2)
    f_abs = np.abs(f)
    # ピーク検出
    peak_args = argrelmax(f_abs[:(int)(chunk/2)])
    f_peak = f_abs[peak_args]
    f_peak_argsort = f_peak.argsort()[::-1]
    peak_args_sort = peak_args[0][f_peak_argsort]
    # 最大ピークをreturn
    return freq[peak_args_sort[0]]


def detectTonesInOctave(freq_in):
    isFirst = isSecond = isThird = False

    # 検知した周波数が第1音、第2音、第3音のX倍音なのか調べる
    octave_first = freq_in / FIRST_FREQ
    octave_second = freq_in / SECOND_FREQ
    octave_third = freq_in / THIRD_FREQ
    near_oct_first = round(octave_first)
    near_oct_second = round(octave_second)
    near_oct_third = round(octave_third)

    if near_oct_first == 0 or near_oct_second == 0 or near_oct_third == 0:
        return False, False, False

    # X倍音のXが整数からどれだけ離れているか
    err_first = np.abs((octave_first - near_oct_first) / near_oct_first)
    err_second = np.abs((octave_second - near_oct_second) / near_oct_second)
    err_third = np.abs((octave_third - near_oct_third) / near_oct_third)

    # 基音、2倍音、3倍音の付近であればインターホンの音とする
    if err_first < FREQ_ERR:
        isFirst = True
    elif err_second < FREQ_ERR and detect_first:
        isSecond = True
    elif err_third < FREQ_ERR and detect_second:
        isThird = True

    return isFirst, isSecond, isThird


if __name__ == '__main__':
    P = pyaudio.PyAudio()
    stream = P.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    frames_per_buffer=CHUNK,
                    input=True,
                    output=False)

    start = time.time()

    while stream.is_active():
        try:
            input = stream.read(CHUNK, exception_on_overflow=False)
            ndarray = np.frombuffer(input, dtype='int16')
            abs_array = np.abs(ndarray)/32768

            if abs_array.max() > 0.1:
                # FFTで最大振幅の周波数を取得
                freq_max = getMaxFreqFFT(ndarray, CHUNK, freq)
                print("振幅最大の周波数:", freq_max, "Hz")

                f, s, t = detectTonesInOctave(freq_max)

                if f:
                    start = time.time()
                    detect_first = True
                    print("第1音検知")
                    continue

                if s:
                    detect_second = True
                    print("第2音検知")
                    continue
                if t:
                    detect_third = True
                    print("第3音検知")

                if detect_first and detect_second and detect_third:
                    print("インターホンの音を感知")
                    time.sleep(5)
                    print("リセット")
                    detect_first = detect_second = detect_third = False

                elapsed_time = time.time() - start
                if detect_first and elapsed_time > 2:
                    print("時間切れによるリセット")
                    detect_first = detect_second = detect_third = False

        except KeyboardInterrupt:
            break

    stream.stop_stream()
    stream.close()
    P.terminate()
