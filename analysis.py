import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt

#音声ファイル読み込み
wav_filename = './ドアベル.wav'
rate, data = scipy.io.wavfile.read(wav_filename)

##### 音声データをそのまま表示する #####
#縦軸（振幅）の配列を作成   #16bitの音声ファイルのデータを-1から1に正規化
data = data / 32768
#横軸（時間）の配列を作成　　#np.arange(初項, 等差数列の終点, 等差)
time = np.arange(0, data.shape[0]/rate, 1/rate)  
#データプロット
plt.plot(time, data)
plt.show()

##### 周波数成分を表示する #####
#縦軸：dataを高速フーリエ変換する（時間領域から周波数領域に変換する）
fft_data = np.abs(np.fft.fft(data))    
#横軸：周波数の取得　　#np.fft.fftfreq(データ点数, サンプリング周期)
freqList = np.fft.fftfreq(data.shape[0], d=1.0/rate)  
#データプロット
plt.plot(freqList, fft_data)
plt.xlim(0, 8000) #0～8000Hzまで表示
plt.show()

#解析結果
#587 Hz
#740 Hz
#880 Hz

# print(rate) 
# ##### 音声データをそのまま表示する #####
# #縦軸（振幅）の配列を作成   #16bitの音声ファイルのデータを-1から1に正規化
# data = data / 32768
# #横軸（時間）の配列を作成　　#np.arange(初項, 等差数列の終点, 等差)
# time = np.arange(0, data.shape[0]/rate, 1/rate)  
# #データプロット
# plt.plot(time, data)
# plt.show()