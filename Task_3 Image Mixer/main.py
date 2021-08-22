from PyQt5 import QtWidgets ,QtCore,QtGui
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,QAction, QFileDialog, QApplication,QSlider , QMessageBox)
from ImageMixer import Ui_MainWindow
from scipy.ndimage import interpolation
from imageModel import ImageModel
from modesEnum import Modes
import logging
import numpy as np
import cv2 
import sys
import os


class ApplicationWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(ApplicationWindow , self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.imageWidgets =[[self.ui.Image1 , self.ui.Image2],[ self.ui.Image1Component , self.ui.Image2Component,],[self.ui.Output1, self.ui.Output2]]
        self.Image_Comp_Boxes = [self.ui.Image1Comp,self.ui.Image2Comp]
        self.choose_image =[self.ui.Image1ComboBox,self.ui.Image2ComboBox]
        self.sliderLabels=[self.ui.showValue1,self.ui.showValue2]
        self.component_boxes = [self.ui.Component1Box , self.ui.Component2Box]
        self.sliders=[self.ui.Slider1,self.ui.Slider2]
        logging.basicConfig(filename='LoggingFile.log' , level=logging.INFO , format='%(levelname)s:%(message)s')
        
        for i in range(len(self.imageWidgets)):
            for j in range(len(self.imageWidgets)-1):
                self.imageWidgets[i][j].ui.histogram.hide()
                self.imageWidgets[i][j].ui.roiBtn.hide()
                self.imageWidgets[i][j].ui.menuBtn.hide()
                self.imageWidgets[i][j].ui.roiPlot.hide()
        
        self.spectrums = [lambda: self.Image_spectrum(0),lambda:self.Image_spectrum(1)]
        self.choose_comp = [lambda:self.choose_component(0),lambda:self.choose_component(1)]
        self.read_value = [lambda: self.sliderValue(0) , lambda: self.sliderValue(1)]
        self.get_value=[lambda:self.combobox_value(0),lambda:self.combobox_value(1)]

        for i in range(2):
            self.Image_Comp_Boxes[i].setEnabled(False)
            self.Image_Comp_Boxes[i].activated.connect(self.spectrums[i])
            self.choose_image[i].activated.connect(self.choose_comp[i])
            self.choose_image[i].setEnabled(False)
            self.component_boxes[i].activated.connect(self.get_value[i])
            self.component_boxes[i].setEnabled(False)
            self.sliders[i].valueChanged.connect(self.read_value[i])
        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionsave.triggered.connect(self.save)
        self.ui.OutPut_Box.activated.connect(self.output)

        self.selectImage = 0
        self.plot=[]
        self.colored_plot =[]
        self.comboboxes =['' , '']
        self.slider_values=[0,0]
        self.imgSize=[0,0]
        self.images = [[] for i in range(2)]
        self.image_fft=[[] for i in range(2)]
        self.image_shift =[[] for i in range(2)]
        self.components=[[] for i in range(2)]
        self.objects=[] 
        self.indecis=[0,0]


    def open(self):
        if self.selectImage>1:
            self.images = [[] for i in range(2)]
            self.selectImage=0
            self.objects=[]
            for i in range(len(self.imageWidgets)):
                for j in range(len(self.imageWidgets)-1):
                    self.imageWidgets[i][j].clear()
            

        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if filePath != "":
            if self.selectImage==0:
                logging.info('Opening Image0')
                self.image_path1=filePath
                self.objects.append(ImageModel(self.image_path1))
                self.images[self.selectImage]=self.objects[self.selectImage].imgByte
                self.imgSize[self.selectImage] = self.images[self.selectImage].shape

            if self.selectImage==1:
                logging.info('Opening Image1')
                self.image_path2=filePath
                self.image2=cv2.imread(self.image_path2 , 0)
                self.imgSize[self.selectImage] = self.image2.shape
                if self.imgSize[0] != self.imgSize[1]:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText('Size Does Not Match')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                else:
                    self.objects.append(ImageModel(self.image_path2))
                    self.images[self.selectImage]=self.objects[self.selectImage].imgByte
            self.showImage()
            
            
           
        
    def showImage(self):
        if self.images[self.selectImage] != []:
            
            self.imageWidgets[1][self.selectImage].clear()
            self.imageWidgets[0][self.selectImage].show()
            self.Image_Comp_Boxes[self.selectImage].setEnabled(True)
            self.choose_image[self.selectImage].setEnabled(True) 
            self.imageWidgets[0][self.selectImage].setImage(self.images[self.selectImage].T)
            if self.selectImage == 0:
                logging.info('Displaying Image0')
            else:
                logging.info('Displaying Image1')
            
            self.selectImage +=1




    def Image_spectrum(self,i):
        
        if self.Image_Comp_Boxes[i].currentText()=='Magnitude Spectral' :
            self.displayed_component=20*np.log(self.objects[i].magnitude)
            logging.info('Displaying Magnitude Spectral')
        elif self.Image_Comp_Boxes[i].currentText()=='Phase Spectral' :
            self.displayed_component=self.objects[i].phase
            logging.info('Displaying Phase Spectral')
        elif self.Image_Comp_Boxes[i].currentText()=='Real Component' :
            self.displayed_component=self.objects[i].real
            logging.info('Displaying Real Spectral of Image')
        elif self.Image_Comp_Boxes[i].currentText()=='Imaginary Component':
            self.displayed_component=self.objects[i].imaginary
            logging.info('Displaying Imaginary Spectral of Image')
        self.imageWidgets[1][i].show()
        self.imageWidgets[1][i].setImage(self.displayed_component.T)
        print(self.displayed_component.dtype)


    def choose_component(self,i):
        logging.info('Choosing component')
        self.component_boxes[i].setEnabled(True)
        self.component_boxes[i].setCurrentIndex(0)
        self.indecis[i]=self.choose_image[i].currentIndex()
        if self.indecis[i] == 0:
            logging.info('Choosing Image 1 as component')
        else:
            logging.info('Choosing Image 2 as component')
        
    

    def combobox_value(self,i):
        self.comboboxes[i]=self.component_boxes[i].currentText()
        if i ==0:
            self.imageWidgets[2][self.ui.OutPut_Box.currentIndex()].clear()
            self.component_boxes[1].setCurrentIndex(0)
            self.comboboxes=[self.comboboxes[i] , '']
        logging.info('Selecting the spectral of component' )
        if self.comboboxes==['' , self.comboboxes[i]]:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Pay Attention!")
            msg.setInformativeText('Chosse Spectrum for Image1 First')
            msg.setWindowTitle("Warning")
            msg.exec_()

        
        if self.comboboxes[0]=='Magnitude' or self.comboboxes[0]=='Uniform Magnitude':
            self.component_boxes[1].view().setRowHidden(1,False)
            self.component_boxes[1].view().setRowHidden(2,True)
            self.component_boxes[1].view().setRowHidden(3,True)
            self.component_boxes[1].view().setRowHidden(5,True)
            self.component_boxes[1].view().setRowHidden(6,True)
        if self.comboboxes[0]=='Phase' or self.comboboxes[0]=='Uniform Phase' :
            self.component_boxes[1].view().setRowHidden(1,True)
            self.component_boxes[1].view().setRowHidden(2,False)
            self.component_boxes[1].view().setRowHidden(3,False)
            self.component_boxes[1].view().setRowHidden(4,True)
            self.component_boxes[1].view().setRowHidden(5,True)
            self.component_boxes[1].view().setRowHidden(6,True)
        if self.comboboxes[0]=='Real':
            self.component_boxes[1].view().setRowHidden(1,True)
            self.component_boxes[1].view().setRowHidden(2,True)
            self.component_boxes[1].view().setRowHidden(3,True)
            self.component_boxes[1].view().setRowHidden(4,True)
            self.component_boxes[1].view().setRowHidden(5,True)
            self.component_boxes[1].view().setRowHidden(6,False)
        if self.comboboxes[0]=='Imaginary':
            self.component_boxes[1].view().setRowHidden(1,True)
            self.component_boxes[1].view().setRowHidden(2,True)
            self.component_boxes[1].view().setRowHidden(3,True)
            self.component_boxes[1].view().setRowHidden(4,True)
            self.component_boxes[1].view().setRowHidden(5,False)
            self.component_boxes[1].view().setRowHidden(6,True)
        self.sliderValue(i)


    def sliderValue (self,i):
        logging.info('Changing Slider Value')
        self.slider_values[i] = (self.sliders[i].value()/100)
        self.sliderLabels[i].setText(str(self.slider_values[i]))
        self.mix_spectrums()
       



    def mix_spectrums (self):
       
        if self.comboboxes[0]=="Magnitude" and self.comboboxes[1]=="Phase":
            mode= Modes.magnitudeAndPhase
            self.plot=self.objects[self.indecis[0]].mix( self.objects[self.indecis[1]] , self.slider_values[0] ,self.slider_values[1] , mode)
            
        elif self.comboboxes[0]=="Magnitude" and self.comboboxes[1]=="Uniform Phase": 
            mode=Modes.magnitudeAndUniformPhase
            self.plot=self.objects[self.indecis[0]].mix( self.objects[self.indecis[1]] , self.slider_values[0] ,self.slider_values[1] , mode)
        elif self.comboboxes[0]=="Uniform Magnitude" and self.comboboxes[1]=="Uniform Phase":
            mode=Modes.UniformMagnitudeAndUniformPhase
            self.plot=self.objects[self.indecis[0]].mix( self.objects[self.indecis[1]] , self.slider_values[0] ,self.slider_values[1] , mode)
        elif self.comboboxes[0]=="Uniform Magnitude" and self.comboboxes[1]=="Phase":
            mode=Modes.UniformMagnitudeandPhase
            self.plot=self.objects[self.indecis[0]].mix( self.objects[self.indecis[1]] , self.slider_values[0] ,self.slider_values[1] , mode)
        elif self.comboboxes[0]=="Real" and self.comboboxes[1]=="Imaginary":
            mode=Modes.realAndImaginary
            self.plot=self.objects[self.indecis[0]].mix( self.objects[self.indecis[1]] , self.slider_values[0] ,self.slider_values[1] , mode)


        
        elif self.comboboxes[1]=="Magnitude" and self.comboboxes[0]=="Phase":
            mode= Modes.magnitudeAndPhase
            self.plot=self.objects[self.indecis[1]].mix( self.objects[self.indecis[0]] , self.slider_values[1] ,self.slider_values[0] , mode)
        elif self.comboboxes[1]=="Magnitude" and self.comboboxes[0]=="Uniform Phase": 
            mode=Modes.magnitudeAndUniformPhase
            self.plot=self.objects[self.indecis[1]].mix( self.objects[self.indecis[0]] , self.slider_values[1] ,self.slider_values[0] , mode)
        elif self.comboboxes[1]=="Uniform Magnitude" and self.comboboxes[0]=="Uniform Phase":
            mode=Modes.UniformMagnitudeAndUniformPhase
            self.plot=self.objects[self.indecis[1]].mix( self.objects[self.indecis[0]] , self.slider_values[1] ,self.slider_values[0] , mode)
        elif self.comboboxes[1]=="Uniform Magnitude" and self.comboboxes[0]=="Phase":
            mode=Modes.UniformMagnitudeandPhase
            self.plot=self.objects[self.indecis[1]].mix( self.objects[self.indecis[0]] , self.slider_values[1] ,self.slider_values[0] , mode)
        elif self.comboboxes[1]=="Real" and self.comboboxes[0]=="Imaginary":
            mode=Modes.realAndImaginary
            self.plot=self.objects[self.indecis[1]].mix( self.objects[self.indecis[0]] , self.slider_values[1] ,self.slider_values[0] , mode)

        
        else: 
            logging.info('Non Well Specified Spectrums')
        if self.plot != []:
            self.output()
      
        

    def output(self):
        
        self.imageWidgets[2][self.ui.OutPut_Box.currentIndex()].show()
        self.imageWidgets[2][self.ui.OutPut_Box.currentIndex()].setImage((self.plot).T)

    def save(self):
        path=os.path.dirname(self.image_path1)
        x=cv2.imwrite(os.path.join(str(path) , 'MixedImage.png'),self.plot)
        print(x)
        



def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()
if __name__ == "__main__":
    main()

    
        
