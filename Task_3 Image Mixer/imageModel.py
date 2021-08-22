## This is the abstract class that the students should implement  

from modesEnum import Modes
import numpy as np
import cv2

class ImageModel():

    """
    A class that represents the ImageModel"
    """

    def __init__(self):
        pass

    def __init__(self, imgPath: str):
        self.imgPath = imgPath
        ###
        # ALL the following properties should be assigned correctly after reading imgPath 
        ###
        self.imgByte =cv2.imread(self.imgPath , 0)
        self.dft = np.fft.fft2(self.imgByte)
        self.real = np.real(self.dft)
        self.imaginary = np.imag(self.dft)
        self.magnitude = np.abs(self.dft)
        self.phase = np.angle(self.dft)
        
    def mix(self, imageToBeMixed: 'ImageModel', magnitudeOrRealRatio: float, phaesOrImaginaryRatio: float, mode: 'Modes') -> np.ndarray:
        """
        a function that takes ImageModel object mag ratio, phase ration 
        """
        ### 
        # implement this function
        ###
        if mode==Modes.magnitudeAndPhase:
            #self.new_magnitude=cv2.addWeighted(self.magnitude,magnitudeOrRealRatio,imageToBeMixed.magnitude,1-magnitudeOrRealRatio,0)
            new_magnitude=((self.magnitude)*(magnitudeOrRealRatio))+((imageToBeMixed.magnitude)*(1-magnitudeOrRealRatio))
            #self.new_phase=cv2.addWeighted(imageToBeMixed.phase,phaesOrImaginaryRatio,self.phase,1-phaesOrImaginaryRatio,0)
            new_phase=((imageToBeMixed.phase)*(phaesOrImaginaryRatio))+((1-phaesOrImaginaryRatio)*self.phase)
            vectorized = np.vectorize(complex)
            mixed_image=new_magnitude*(np.exp(vectorized(0,new_phase)))



        elif mode == Modes.magnitudeAndUniformPhase:
            new_magnitude=((self.magnitude)*(magnitudeOrRealRatio))+((imageToBeMixed.magnitude)*(1-magnitudeOrRealRatio))
            new_phase = np.zeros(self.imgByte.shape)
            vectorized = np.vectorize(complex)
            mixed_image=new_magnitude*(np.exp(vectorized(0,new_phase)))



        elif mode == Modes.UniformMagnitudeAndUniformPhase:
            new_magnitude=np.ones(self.imgByte.shape)
            new_phase = np.zeros(self.imgByte.shape)
            vectorized = np.vectorize(complex)
            mixed_image=new_magnitude*(np.exp(vectorized(0,new_phase)))


        elif mode==Modes.UniformMagnitudeandPhase:
            new_magnitude=np.ones(self.imgByte.shape)
            new_phase=((imageToBeMixed.phase)*(phaesOrImaginaryRatio))+((1-phaesOrImaginaryRatio)*self.phase)
            vectorized = np.vectorize(complex)
            mixed_image=new_magnitude*(np.exp(vectorized(0,new_phase)))

        elif mode == Modes.realAndImaginary:
            new_real = cv2.addWeighted(self.real,magnitudeOrRealRatio,imageToBeMixed.real,1-magnitudeOrRealRatio,0)
            new_imaginary = cv2.addWeighted(self.imaginary,magnitudeOrRealRatio,imageToBeMixed.imaginary,1-magnitudeOrRealRatio,0)
            vectorized = np.vectorize(complex)
            mixed_image = new_real + (1j*(vectorized(0,new_imaginary)))
        
        inverse_mix = np.fft.ifft2(mixed_image)
        
        return ((np.real(inverse_mix)))