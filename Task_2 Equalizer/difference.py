##### DIFFERENCE ######

self.ui.actionFFT_Difference_2.triggered.connect(self.plot_diff)

def plot_diff(self):
        self.win = pg.GraphicsWindow()
        self.win.show()
        p1 = self.win.addPlot()
        self.yaxis = fftpack.irfft(self.FT-self.FT2).astype(self.data_type)
        p1.plot(self.time,self.yaxis) 