##################################################
#                                                #
# IV testing at 15mV                             #
#                                                #
# Larry Gardner, July 2018                       #         
#                                                #
##################################################

import sys
import pyoo
import os
from math import *
import DAQ
import matplotlib.pyplot as plt



class IV:
    def __init__(self):
        self.Vdata = []
        self.Idata = []
        
        self.v1 = float(input("Maximum voltage: "))
        self.v2 = float(input("Minimum voltage: "))
        self.step = float(input("Step: "))
        self.Navg = int(input("Averaging factor: ")) + 1
        self.use = "IV.use"
        
        if self.v1 < self.v2:
            self.v1, self.v2 = self.v2, self.v1
     
    def readFile(self):
        # Opens use file and assigns corresponding parameters
        f = open(self.use, 'r')
        lines = f.readlines()
        f.close()
        
        self.Vs_min = float(lines[0].split()[0])
        self.Vs_max = float(lines[1].split()[0])
        self.MaxDAC = float(lines[2].split()[0])
        self.ADRate = int(lines[3].split()[0])
        self.G1 = float(lines[4].split()[0])
        self.G2 = float(lines[5].split()[0])
        self.Boardnum = int(lines[6].split()[0])
        #self.AD_GAIN = int(lines[7].split()[0])
        #self.Poffset = float(lines[8].split()[0])
        
        self.Vrange = self.Vs_max - self.Vs_min
        self.n0 = self.MaxDAC / self.Vrange
        self.nn = int(floor((self.Vs_max - self.v1) * self.n0))
    
    def crop(self):
        # Limits voltages to Vmax and Vmin
        if self.v1 < self.Vs_min:
            self.v1 = self.Vs_min
        if self.v1 > self.Vs_max:
            self.v1 = self.Vs_max
        if self.v2 < self.Vs_min:
            self.v2 = self.Vs_min
        if self.v2 > self.Vs_max:
            self.v2 = self.Vs_max
            
    def initDAQ(self):
        # Lists available DAQ devices and connects the selected board
        self.daq = DAQ.DAQ()
        self.daq.listDevices()
        self.daq.connect(self.Boardnum)
    
    def endDAQ(self):
        # Disconnects and releases selected board number
        self.daq.disconnect(self.Boardnum)
    
    def readVolt(self, channel = 0):
        # Reads voltage
        volt = self.daq.AIn(channel)
        volt = (volt/G1)*1000
        return volt
    
    def setSweep(self):
        print("Preparing for sweep...")
        # Sets variables in preparation for sweep
        self.crop()
        self.Vrange = self.Vs_max - self.Vs_min
        self.n0 = self.MaxDAC / self.Vrange

    def setBias(self, volt, channel = 0):
        print("\nSetting bias voltage...")
        self.nn = int(floor((self.Vs_max - volt) * self.n0))
        self.daq.AOut(self.nn, channel)
        reading = self.readVolt(channel)
        while (abs(reading - self.v1) > .2):
            if (volts < v1):
                self.nn -= 1
            else:
                nn += 1
            if self.nn >= self.MaxDAC:
                self.nn = self.MaxDAC - 1
            self.daq.AOut(self.nn, channel)
            reading = self.readVolt(channel)
        
    def runSweep(self):
        print("\nRunning sweep...")
        
        
       
       
       
       
       
    def spreadsheet(self, save_name = "IVtest"):
        print("\nWriting data to spreadsheet...")
        
        # Creates localhost for libre office
        os.system("soffice --accept='socket,host=localhost,port=2002;urp;' --norestore --nologo --nodefault # --headless")
        
        # Uses pyoo to open spreadsheet
        desktop = pyoo.Desktop('localhost',2002)
        doc = desktop.create_spreadsheet()

        # Writes data to spreadsheet
        sheet = doc.sheets[0]
        sheet[0,0:2].values = ["Voltage (mV)","Current (mA)"]
        sheet[1:len(self.Vdata)+1, 0].values = self.Vdata
        sheet[1:len(self.Idata)+1, 1].values = self.Idata
        doc.save('IVData/' + str(save_name) + '.xlsx')
        doc.close()
    
    def plotIV(self):
        # Plot IV curve
        plt.plot(self.Vdata,self.Idata, 'ro-')
        plt.xlabel("Voltage (mV)")
        plt.ylabel("Current (mA)")
        plt.axis([min(self.Vdata), max(self.Vdata), min(self.Idata), max(self.Idata)])
        plt.show()
   
          
if __name__ == "__main__":
    test = IV()
    test.readFile()
    test.initDAQ()
    test.setSweep()
    test.setBias(test.v1)
    
    
    test.setBias(0)
    #test.spreadsheet()
    test.endDAQ()
    #test.plotIV()
    
    print("\nEnd.")