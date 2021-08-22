from PyQt5 import QtWidgets ,QtCore,QtGui
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,QAction, QFileDialog, QApplication,QSlider,QTabWidget,QWidget,QTableWidget,QTableWidgetItem)
from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
import os, sys
import numpy as np
from scipy import fftpack
import pyqtgraph as pg
import matplotlib.pyplot as plt
from Task4 import Ui_MainWindow
import librosa
import librosa.display
from os import path
from pydub import AudioSegment
import sounddevice as sd
import glob
import imagehash
from PIL import Image
import hashlib
import csv
import pandas as pd
import difflib
from operator import itemgetter



class ApplicationWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(ApplicationWindow,self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.actionOpen_Song_1.triggered.connect(self.OpenSong)
		self.ui.Slider.valueChanged.connect(self.mix)
		self.flag = False
		self.radiobuttons = [self.ui.Hashing,self.ui.Features]
		for i in range(2):
			self.radiobuttons[i].toggled.connect(self.mix)

	def OpenSong(self):
		self.filePath = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', 'C:\\Users\\Dr.Ahmed\\Desktop\\Task 4')
		self.Audio_Convert_Cut(self.filePath[0])
		self.Spectrogram_Creation()
		if self.flag == False:
			self.flag = True
		elif self.flag == True:
			self.flag = False

	def mix(self):
		self.ratio = float(self.ui.Slider.value()/100)
		self.mixed = (self.ratio * self.Song_1) + ( (1 - self.ratio) * self.Song_2)
		sd.play(self.mixed,22050)
		hop_length = 512
		window_size = 1024
		window = np.hanning(window_size)
		stft  = librosa.core.spectrum.stft(self.mixed, n_fft = window_size, hop_length = hop_length,window=window)
		out = 2 * np.abs(stft) / np.sum(window)
		librosa.display.specshow(librosa.amplitude_to_db(out,ref=np.max), y_axis='log', x_axis='time')
		self.MixHash = self.Hashing(out)
		self.MixFeat = self.Features(self.mixed,22050)
		self.Mix_List = [self.MixHash[0],self.MixFeat[0],self.MixFeat[1],self.MixFeat[2],self.MixFeat[3],self.MixFeat[4]]
		self.Comparison_method()

	def Audio_Convert_Cut(self,path):
		if self.flag == False:
			dst = "test.wav"
			sound = AudioSegment.from_mp3(path)
			sound.export(dst, format="wav")
			newAudio = AudioSegment.from_wav("test.wav")
			newAudio = newAudio[0:60*1000]
			newAudio.export('new_m.wav', format="wav")
	
		elif self.flag == True:
			dst = "test1.wav"
			sound = AudioSegment.from_mp3(path)
			sound.export(dst, format="wav")
			newAudio = AudioSegment.from_wav("test1.wav")
			newAudio = newAudio[0:60*1000]
			newAudio.export('new_m1.wav', format="wav")

	def Spectrogram_Creation(self):
		hop_length = 512
		window_size = 1024
		if self.flag == False:
			y, sr = librosa.load('new_m.wav')
			self.Song_1 = y
		elif self.flag == True:
			y, sr = librosa.load('new_m1.wav')
			self.Song_2 = y
		window = np.hanning(window_size)
		stft  = librosa.core.spectrum.stft(y, n_fft = window_size, hop_length = hop_length,window=window)
		out = 2 * np.abs(stft) / np.sum(window)
		librosa.display.specshow(librosa.amplitude_to_db(out,ref=np.max), y_axis='log', x_axis='time')
		self.Hashing(out)
		self.Features(y,sr)

	def Hashing(self,Spectro_array):
		img = Image.fromarray(Spectro_array,mode = 'RGB')
		hashing = imagehash.phash(img)
		hashing = [str(hashing)]
		return hashing

	def Features(self,data,sr):
		X = librosa.stft(data)
		X_abs = np.abs(X)
		X_abs_Trans = X_abs.T
		XDB = librosa.amplitude_to_db(X_abs , ref=np.max)

		#Spectral Centroids :
		spectral_centr = librosa.feature.spectral_centroid(S = X_abs,sr = sr)
		centroid = Image.fromarray(spectral_centr,mode = 'RGB')
		centroid_hash = str(imagehash.phash(centroid))

		#Spectral Roll-Off :
		spectral_rollOff = librosa.feature.spectral_rolloff(S =X_abs , sr = sr)
		rolloff = Image.fromarray(spectral_rollOff,mode = 'RGB')
		rolloff_hash = str(imagehash.phash(rolloff))

		#Spectral Bandwidth :
		spectral_bandwidth = librosa.feature.spectral_bandwidth(S = X_abs, sr = sr)
		bandwidth = Image.fromarray(spectral_bandwidth,mode = 'RGB')
		bandwidth_hash = str(imagehash.phash(bandwidth))
		
		#MEl-Scaled Power Spectrogram :
		Mel_scaled_spectrogram = librosa.feature.melspectrogram(S=(X_abs **2) , sr=sr)
		mel = Image.fromarray(Mel_scaled_spectrogram,mode = 'RGB')
		mel_hash = str(imagehash.phash(mel))

		#Chroma feature :
		chroma_feature = librosa.feature.chroma_stft(S= X_abs , sr=sr)
		chroma = Image.fromarray(chroma_feature,mode = 'RGB')
		chroma_hash = str(imagehash.phash(chroma))
		
		self.Features_list = [centroid_hash,rolloff_hash,bandwidth_hash,mel_hash,chroma_hash]
		return self.Features_list

	def Data_Display(self,Data):
			numrows = 10 
			numcols = 2  
			for row in range(numrows):
				for column in range(numcols):
					self.ui.tableWidget.setItem(row, column, QTableWidgetItem((Data[row][column])))

	def Comparison_method(self):
		self.dirs = os.listdir('Spectrograms/New_Songs/')
		self.Spectro_Data = []
		self.Features_Data = []
		if self.radiobuttons[0].isChecked():
			self.xd1 = pd.read_csv('Spectro.csv')
			self.hashes = self.xd1.iloc[:,0]
			for i in range(len(self.hashes)):
				self.similarity_percentage = difflib.SequenceMatcher(None,str(self.Mix_List[0]), str(self.hashes[i])).ratio()
				self.Final = [self.dirs[i],str(self.similarity_percentage)]
				self.Spectro_Data.append(self.Final)
			self.Spectro_Data = sorted(self.Spectro_Data, key = itemgetter(1) ,reverse = True)
			self.Spectro_Data = self.Spectro_Data[:10]
			self.Data_Display(self.Spectro_Data)
			
			
		elif self.radiobuttons[1].isChecked():
			self.xd2 = pd.read_csv(('Features.csv'))
			self.feat1 = self.xd2.iloc[:,0]
			self.feat2 = self.xd2.iloc[:,1]
			self.feat3 = self.xd2.iloc[:,2]
			self.feat4 = self.xd2.iloc[:,3]
			self.feat5 = self.xd2.iloc[:,4]
			for i in range(len(self.feat5)):
				sim_per1 = difflib.SequenceMatcher(None,str(self.Mix_List[1]), str(self.feat1[i])).ratio()
				sim_per2 = difflib.SequenceMatcher(None,str(self.Mix_List[2]), str(self.feat2[i])).ratio()
				sim_per3 = difflib.SequenceMatcher(None,str(self.Mix_List[3]), str(self.feat3[i])).ratio()
				sim_per4 = difflib.SequenceMatcher(None,str(self.Mix_List[4]), str(self.feat4[i])).ratio()
				sim_per5 = difflib.SequenceMatcher(None,str(self.Mix_List[5]), str(self.feat5[i])).ratio()
				self.average = float((sim_per1 + sim_per2 + sim_per3 + sim_per4 + sim_per5)/5)
				self.Final_1 = [self.dirs[i],str(self.average)]
				self.Features_Data.append(self.Final_1)
			self.Features_Data = sorted(self.Features_Data, key = itemgetter(1) ,reverse = True)
			self.Features_Data = self.Features_Data[:10]
			self.Data_Display(self.Features_Data)


def main():
	app = QtWidgets.QApplication(sys.argv)
	application = ApplicationWindow()
	application.show()
	app.exec_()
if __name__ == "__main__":
	main()