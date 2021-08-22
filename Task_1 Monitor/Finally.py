from PyQt5 import QtWidgets,QtCore
from FINAL_DESIGN import Ui_MainWindow
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,QAction, QFileDialog, QApplication)
import sys
import pandas as pd
import pyqtgraph as pg
from scipy.io import wavfile
import numpy as np

class ApplicationWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.flag = [True for i in range(5)]
        self.slicer = [ 0 for i in range(5)]
        self.xd = [[0] for i in range(5)] 
        self.data_line =[0 for i in range(5)]
        self.selectChannel = 0
        self.mob_checker = True
        self.Channels = [self.ui.channel1,self.ui.channel2,self.ui.channel3,self.ui.channel4,self.ui.channel5]
        self.radioButtons = [self.ui.radioButton_1, self.ui.radioButton_2, self.ui.radioButton_3, self.ui.radioButton_4, self.ui.radioButton_5]
        for i in range(5):
            self.radioButtons[i].toggled.connect(self.Buttons_Activation)
        
        self.ui.hide1.clicked.connect(self.hide1)        
        self.ui.hide2.clicked.connect(self.hide2)
        self.ui.hide3.clicked.connect(self.hide3)
        self.ui.hide4.clicked.connect(self.hide4)
        self.ui.hide5.clicked.connect(self.hide5)
        
        self.ui.play_btn.clicked.connect(self.play)
        self.ui.stop_btn.clicked.connect(self.stop)
        self.ui.pause_btn.clicked.connect(self.pause)
        self.ui.zoom_in.clicked.connect(self.zoomin)
        self.ui.zoom_out.clicked.connect(self.zoomout)
        self.ui.add_signal.clicked.connect(self.browser)
        self.ui.pushButton_6.clicked.connect(self.AddChannel)
        
        self.pen1 = pg.mkPen(color=(255, 0, 0))
        self.pen2 = pg.mkPen(color=(255, 204, 0))
        self.pen3 = pg.mkPen(color=(204, 0, 204))
        self.pen4 = pg.mkPen(color=(0, 255, 0))
        self.pen5 = pg.mkPen(color=(0, 0, 255))
        
        
        self.timer1 = QtCore.QTimer()
        self.timer5 = QtCore.QTimer()
        self.timer2 = QtCore.QTimer()
        self.timer3 = QtCore.QTimer()
        self.timer4 = QtCore.QTimer()
        
        self.timer1.setInterval(50)
        self.timer2.setInterval(50)
        self.timer3.setInterval(50)
        self.timer4.setInterval(50)
        self.timer5.setInterval(50)

        self.timer1.timeout.connect(self.update_plot_data1)
        self.timer2.timeout.connect(self.update_plot_data2)
        self.timer3.timeout.connect(self.update_plot_data3)
        self.timer4.timeout.connect(self.update_plot_data4)
        self.timer5.timeout.connect(self.update_plot_data5)

        self.timers = [self.timer1,self.timer2,self.timer3,self.timer4,self.timer5]
        self.view = self.Channels[self.selectChannel].plotItem.getViewBox()
       
        
        self.x = [[0] for i in range(5)]
        self.y = [[0] for i in range(5)]
        self.y1 = [[0] for i in range(5)]
        
        self.ui.play_btn.setEnabled(False)
        self.ui.pause_btn.setEnabled(False)
        self.ui.stop_btn.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False) 
        self.ui.zoom_in.setEnabled(False)
        self.ui.zoom_out.setEnabled(False)
        self.ui.add_signal.setEnabled(False)
                
    def select(self):
        if self.radioButtons[0].isChecked():
            self.selectChannel = 0
            
            
        if self.radioButtons[1].isChecked():
            self.selectChannel = 1
           
            
        if self.radioButtons[2].isChecked():
            self.selectChannel = 2

        if self.radioButtons[3].isChecked():
            self.selectChannel = 3

        if self.radioButtons[4].isChecked():
            self.selectChannel = 4
        
    def zoomin(self):
        self.Channels[self.selectChannel].plotItem.getViewBox().scaleBy(0.3)
        self.mob_checker == False

        
    def zoomout(self):
        self.Channels[self.selectChannel].plotItem.getViewBox().scaleBy(1/0.3)
        self.mob_checker == False
        
    def hide1(self):
        self.Channels[0].clear()
        self.Channels[0].hide()
        self.flag[0] = False
    def hide2(self):
        self.Channels[1].clear()
        self.Channels[1].hide()
        self.flag[1] = False
    def hide3(self):
        self.Channels[2].clear()
        self.Channels[2].hide()
        self.flag[2] = False
    def hide4(self):
        self.Channels[3].clear()
        self.Channels[3].hide()
        self.flag[3] = False
    def hide5(self):
        self.Channels[4].clear()
        self.Channels[4].hide()
        self.flag[4] = False
    
    def AddChannel(self):
        for i in range(5):
            if self.flag[i] is False:
                self.Channels[i].show()
                self.flag[i] = True
                break
            
    def play(self):
        #if self.mob_checker == False:
        self.select()
        self.timers[self.selectChannel].start()
        #self.mob_checker = True 
           
    def pause(self):

        #if self.mob_checker == True:
        self.timers[self.selectChannel].stop()
        #self.mob_checker = False
           
    def stop(self):
    
        #if self.mob_checker == True:
        self.timers[self.selectChannel].stop()
        self.slicer[self.selectChannel] = 0
      # self.mob_checker = False
 
    def update_plot_data1(self):
        self.select()
        self.slicer[0] += 10
        self.y1[0] = self.y[0][:self.slicer[0]]
        self.data_line[0].setData(self.y1[0],pen=self.pen1)
        
    def update_plot_data2(self):
        self.select()
        self.slicer[1] += 10
        self.y1[1] = self.y[1][:self.slicer[1]]
        self.data_line[1].setData(self.y1[1],pen=self.pen2)

    def update_plot_data3(self):
        self.select()
        self.slicer[2] += 10
        self.y1[2] = self.y[2][:self.slicer[2]]
        self.data_line[2].setData(self.y1[2],pen=self.pen3)

    def update_plot_data4(self):
        self.select()
        self.slicer[3] += 10
        self.y1[3] = self.y[3][:self.slicer[3]]
        self.data_line[3].setData(self.y1[3],pen=self.pen4)

    def update_plot_data5(self):
        self.select()
        self.slicer[4] += 10
        self.y1[4] = self.y[4][:self.slicer[4]]
        self.data_line[4].setData(self.y1[4],pen=self.pen5)
    
    
    def Buttons_Activation(self, selected):
        if selected:
            self.ui.pause_btn.setEnabled(True)
            self.ui.stop_btn.setEnabled(True)
            self.ui.play_btn.setEnabled(True)
            self.ui.pushButton_6.setEnabled(True)    
            self.ui.zoom_in.setEnabled(True)
            self.ui.zoom_out.setEnabled(True)
            self.ui.add_signal.setEnabled(True)
            

    def browser(self):
        
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.select()
        if filePath != "":
            self.Channels[self.selectChannel].plotItem.clear()
            if filePath.endswith('.txt'):
                self.xd[self.selectChannel] = np.genfromtxt(filePath)
                self.y[self.selectChannel] = self.xd[self.selectChannel][:]
                self.data_line[self.selectChannel] = self.Channels[self.selectChannel].plotItem.plot(self.y[self.selectChannel])
                
                
            elif filePath.endswith('.csv'):
                self.xd[self.selectChannel] = pd.read_csv(str(filePath))
                self.x[self.selectChannel] = self.xd[self.selectChannel].iloc[:,0]
                self.y[self.selectChannel] = self.xd[self.selectChannel].iloc[:,1]
                self.data_line[self.selectChannel] = self.Channels[self.selectChannel].plotItem.plot(self.x[self.selectChannel],self.y[self.selectChannel])
                
                
            elif filePath.endswith('.wav'):
                self.xd[self.selectChannel] = (wavfile.read(filePath))
                self.xd[self.selectChannel] = self.xd[self.selectChannel][1]
                self.y[self.selectChannel] = self.xd[self.selectChannel][:]
                self.data_line[self.selectChannel] = self.Channels[self.selectChannel].plotItem.plot(self.y[self.selectChannel])
            
            self.slicer[self.selectChannel] = 0
            self.timers[self.selectChannel].start()
    
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()

if __name__ == "__main__":
    main()