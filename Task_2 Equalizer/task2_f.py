from PyQt5 import QtWidgets ,QtCore,QtGui
#from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
#import PyQt5.QtMultimediaWidgets as M
from Equalizer1 import Ui_MainWindow
from Sliders2 import Ui_Form
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,QAction, QFileDialog, QApplication,QSlider)
import sys
import time
import pandas as pd
from scipy.io import wavfile
import numpy as np
import pyqtgraph as pg
from scipy import fftpack
import sounddevice as sd


class ApplicationWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionEqualization.triggered.connect(self.Slider_Screen)
        self.ui.actionOpen_File.triggered.connect(self.browser)
        self.ui.actionSave_File.triggered.connect(self.save_file)
        self.ui.actionPlay.triggered.connect(self.playsound)
        self.ui.actionOriginal_Signal.triggered.connect(self.original)
        self.ui.actionFFT_Original.triggered.connect(self.InFT)
        self.ui.actionStop.triggered.connect(self.stopsound)
        self.ui.actionFFT_Input.triggered.connect(self.InFT)
        self.FT = []


    def browser(self):
            filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'F:\25-9\Downloads\talta tebya\Second Semester\DSP\Task2 Equalizer\TASK 2')
            self.drate, self.data = wavfile.read(filePath)    
            self.original()    

    
    def Slider_Screen(self):
        self.Ui = Ui_Form()
        self.InFT()
        self.Form = QtWidgets.QWidget()
        self.Ui.setupUi(self.Form)
        self.Form.show()
        self.Sliders = [self.Ui.Slider1,self.Ui.Slider2,self.Ui.Slider3,self.Ui.Slider4,self.Ui.Slider5,self.Ui.Slider6,self.Ui.Slider7,self.Ui.Slider8,self.Ui.Slider9,self.Ui.Slider10]
        self.SliderFilters = [lambda:self.GainChange(0),lambda:self.GainChange(1),lambda:self.GainChange(2),lambda:self.GainChange(3),lambda:self.GainChange(4),lambda:self.GainChange(5),lambda:self.GainChange(6),lambda:self.GainChange(7),lambda:self.GainChange(8),lambda:self.GainChange(9)]
        self.Windows = [self.Ui.rectangular,self.Ui.hamming,self.Ui.hanning]
        self.Ui.save_btn.clicked.connect(self.save_file)
        self.Ui.play_btn.clicked.connect(self.playsound)
        self.Ui.stop_btn.clicked.connect(self.stopsound)
        self.Ui.reset_btn.clicked.connect(self.Reset)
        self.editted_ampl = []
        #self.n = len(self.hamm)//4
        for i in range(10):
            self.Sliders[i].valueChanged.connect(self.SliderFilters[i]) 
        
        # for i in range(3):
        #     self.Windows[i].toggled.connect(self.GainChange) 

    def original(self):
        self.data_type = self.data.dtype
        if len(self.data.shape) > 1:        #converting to mono
            self.data = np.mean(self.data , axis=1 ).astype(self.data_type)
        self.length = self.data.shape[0]
        self.arrayOfLength = np.arange(self.length)
        #to get time  in x-axis
        self.time = self.arrayOfLength / self.drate
        self.ui.channel1.clear()       
        #for returning the size of the channel
        self.length = self.data.shape[0]
        self.arrayOfLength = np.arange(self.length)
        #to get time  in x-axis
        self.time = self.arrayOfLength / self.drate
        self.ui.channel1.clear()
        self.FT1 = fftpack.rfft(self.data)
        self.FT = self.FT1.copy()
        #print(self.FT)
        self.data_line = self.ui.channel1.plotItem.plot(self.time,self.data)
        self.ui.channel1.setYRange(0,20000)
        self.ui.channel1.setXRange(1,4)
        #self.IFT = fftpack.irfft(self.FT).astype(self.data_type)
        #print(self.IFT.dtype)

    def playsound(self):
        sd.play(fftpack.irfft(self.FT).astype(self.data_type),44100)

    def stopsound(self):
        sd.stop()

    def Reset(self):
        for i in range(10):
            self.Sliders[i].setValue(1)
            
    def InFT(self):
        self.yaxis = np.abs(self.FT)
        self.sampling_freq = self.drate
        self.xaxis =fftpack.rfftfreq(len(self.FT),1/self.sampling_freq)
        self.xaxisabs = np.abs(self.xaxis)
        self.ui.channel2.clear()
        self.data_line1 = self.ui.channel2.plotItem.plot(self.xaxisabs,self.yaxis)

        """ self.win = pg.GraphicsWindow()
        self.win.show()
        p1 = self.win.addPlot()
        p1.plot(self.xaxisabs,self.yaxis) """
        #print(len(self.sound_data))

    def GainChange(self,i):
        self.step = int(len(self.FT1)/10)

        if self.Windows[0].isChecked(): ##rectangular
            self.FT[self.step*i:self.step*(i+1)] = self.Sliders[i].value() * self.FT1[self.step*i:self.step*(i+1)]
            self.Ui.view_edit.clear()
            self.Ui.view_edit.plotItem.plot(self.xaxisabs,self.FT)


        if self.Windows[1].isChecked():
            self.m = int(len(self.FT1[self.step*i:self.step*(i+1)])/2)
            self.hamm = np.hamming(len(self.FT1[self.step*i-self.m: self.step*(i+1)+self.m]))
            self.result = np.multiply(self.hamm , self.FT1[self.step*i-self.m: self.step*(i+1)+self.m])
            self.FT[self.step*i-self.m: self.step*(i+1) + self.m] = self.Sliders[i].value() * self.result
            self.Ui.view_edit.clear()
            self.Ui.view_edit.plotItem.plot(self.xaxisabs,self.FT)

        if self.Windows[2].isChecked():
            self.n = int(len(self.FT1[self.step*i:self.step*(i+1)])/2)
            self.hann = np.hanning(len(self.FT1[self.step*i-self.n: self.step*(i+1)+self.n])) 
            self.result = np.multiply(self.hann , self.FT1[self.step*i-self.m: self.step*(i+1)+self.m])
            self.FT[self.step*i-self.n: self.step*(i+1) + self.n] = self.Sliders[i].value() * self.result
            self.Ui.view_edit.clear()
            self.Ui.view_edit.plotItem.plot(self.xaxisabs,self.FT)
            
        self.IFT = fftpack.irfft(self.FT)
        sd.play(self.IFT.astype(self.data_type),self.drate)

    def save_file(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File','f.wav')
        path = name[0]
        if path!=0:
            wavfile.write(path, self.drate, self.IFT) 

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()
if __name__ == "__main__":
    main()