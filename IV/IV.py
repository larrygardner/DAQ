##################################################
#                                                #
# IV testing                                     #
#                                                #
# Larry Gardner, July 2018                       #         
#                                                #
##################################################

import sys
import pyoo
import os
import time
from math import *
import DAQ
import matplotlib.pyplot as plt


class IV:
    def __init__(self):
        self.Vdata = []
        self.Idata = []
        
        if len(sys.argv) >= 5:
            self.save_name = sys.argv[1]
            self.vmin = float(sys.argv[2])
            self.vmax = float(sys.argv[3])
            self.step = int(sys.argv[4])
            self.Navg = int(sys.argv[5])
            if len(sys.argv) == 7:
                self.use = sys.argv[6]
            else:
                self.use = "IV.use"
        else:
            self.save_name = input("Save name: ")
            self.vmin = float(input("Minimum voltage [mV]: "))
            self.vmax = float(input("Maximum voltage [mV]: "))
            self.step = float(input("Step [mV]: "))
            self.Navg = 10000
            self.use = "IV.use"
        
        if self.vmin > self.vmax:
            self.vmin, self.vmax = self.vmax, self.vmin
     
    def readFile(self):
        # Opens use file and assigns corresponding parameters
        f = open(self.use, 'r')
        lines = f.readlines()
        f.close()
        
        self.Vs_min = float(lines[0].split()[0])
        self.Vs_max = float(lines[1].split()[0])
        self.MaxDAC = float(lines[2].split()[0])
        self.Rate = int(lines[3].split()[0])
        self.G_v = float(lines[4].split()[0])
        self.G_i = float(lines[5].split()[0])
        self.Boardnum = int(lines[6].split()[0])
        self.Range = int(lines[7].split()[0])
        self.Out_channel = int(lines[8].split()[0])
        self.V_channel = int(lines[9].split()[0])
        self.I_channel = int(lines[10].split()[0])
    
    def crop(self):
        # Limits set voltages to max and min sweep voltages
        if self.vmin < self.Vs_min:
            self.vmin = self.Vs_min
        if self.vmin > self.Vs_max:
            self.vmin = self.Vs_max
        if self.vmax < self.Vs_min:
            self.vmax = self.Vs_min
        if self.vmax > self.Vs_max:
            self.vmax = self.Vs_max
            
    def initDAQ(self):
        # Lists available DAQ devices and connects the selected board
        self.daq = DAQ.DAQ()
        self.daq.listDevices()
        self.daq.connect(self.Boardnum)
        
    def readVolt(self, channel = 0):
        # Reads voltage from specified channel
        volt = self.daq.AIn(channel)
        # Converts to mV
        mV = (volt / self.G_v) * 1000
        return mV

    def setBias(self, volt):
        # Sets bias to specified voltage
        self.daq.AOut(volt, self.Out_channel)
        time.sleep(.1)

    def prepSweep(self):
        print("Preparing for sweep...")
        # Prepares for data collection
        self.Vout = []
        self.Iout = []
        self.crop()
        # Setting voltage to max in preparation for sweep
        print("\nChanging voltage to maximum...")
        self.bias = self.vmax
        self.setBias(self.bias / 1000)
        
    def runSweep(self):
        print("\nRunning sweep...")

        # Sets proper format for low and high channels to scan over
        channels = [self.V_channel, self.I_channel]
        low_channel, high_channel = min(channels), max(channels)
        
        index = 0
        while(self.bias > self.vmin):
            self.setBias(self.bias / 1000)
            #Collects data from scan
            data = self.daq.AInScan(low_channel, high_channel, self.Rate, self.Navg)
            # Appends data
            self.Vout.append(data[self.V_channel])
            self.Iout.append(data[self.I_channel])
            # Reformats data
            self.Vout[index] = self.Vout[index] * 1000 * self.G_v
            self.Iout[index] = self.Iout[index] * self.G_i
            
            #if index%10 == 0:
            print(str('\n{:.3}'.format(self.Vout[index])) + ' mV \t{:.3}'.format(str(self.Iout[index])) + ' mA')
            
            self.bias -= self.step
            
            index += 1
            print("INDEX:",index)
            print("BIAS: {:.3}".format(self.bias))
            
        
    def endSweep(self):
        self.bias = 0
        self.setBias(self.bias)
        print("\nBias set to zero. \nSweep is over")
       
    def spreadsheet(self):
        print("\nWriting data to spreadsheet...")
        
        # Creates localhost for libre office
        os.system("soffice --accept='socket,host=localhost,port=2002;urp;' --norestore --nologo --nodefault # --headless")
        
        # Uses pyoo to open spreadsheet
        desktop = pyoo.Desktop('localhost',2002)
        doc = desktop.create_spreadsheet()

        # Writes data to spreadsheet
        sheet = doc.sheets[0]
        sheet[0,0:2].values = ["Voltage (mV)","Current (mA)"]
        sheet[1:len(self.Vout)+1, 0].values = self.Vout
        sheet[1:len(self.Iout)+1, 1].values = self.Iout
        doc.save('IVData/' + str(self.save_name) + '.xlsx')
        doc.close()
    
    def plotIV(self):
        # Plot IV curve
        plt.plot(self.Vdata,self.Idata, 'ro-')
        plt.xlabel("Voltage (mV)")
        plt.ylabel("Current (mA)")
        plt.axis([min(self.Vdata), max(self.Vdata), min(self.Idata), max(self.Idata)])
        plt.show()
    
    def endDAQ(self):
        # Disconnects and releases selected board number
        self.daq.disconnect(self.Boardnum)

    
if __name__ == "__main__":
    test = IV()
    test.readFile()
    test.initDAQ()
    test.prepSweep()
    test.runSweep()
    test.endSweep()
    test.endDAQ()
    test.spreadsheet()
    #test.plotIV()
    
    print("\nEnd.")
