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
import visa
from math import *
import DAQ
import matplotlib.pyplot as plt
import PowerMeter as PM
import gpib


class IV:
    def __init__(self):        
        self.PM = None
        
        if len(sys.argv) >= 5:
            self.save_name = sys.argv[1]
            self.vmin = float(sys.argv[2])
            self.vmax = float(sys.argv[3])
            self.step = int(sys.argv[4])
            if len(sys.argv) == 6:
                self.use = sys.argv[5]
            else:
                self.use = "IV.use"
        else:
            self.save_name = input("Save name: ")
            self.vmin = float(input("Minimum voltage [mV]: "))
            self.vmax = float(input("Maximum voltage [mV]: "))
            self.step = float(input("Step [mV]: "))
            if self.step <= 0:
                while self.step <= 0:
                    print("Step size must be greater than 0.")
                    self.step = float(input("Step [mV]: "))
            self.use = "IV.use"
            
        self.Navg = 10000
        if self.vmin > self.vmax:
            self.vmin, self.vmax = self.vmax, self.vmin
     
    def readFile(self):
        # Opens use file and assigns corresponding parameters
        print("\nUSE file: ",self.use)
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
    
    def initPM(self):
        # Initializes Power Meter
        try:
            rm = visa.ResourceManager("@py")
            lr = rm.list_resources()
            pm = 'GPIB0::12::INSTR'
            if pm in lr:
                self.pm = PM.PowerMeter(rm.open_resource("GPIB0::12::INSTR"))
                self.pm_is_connected = True
                print("Power meter connected.\n")
            else:
                self.pm_is_connected = False
                print("No power meter detected.\n")
        except gpib.GpibError:
            self.pm_is_connected = False
            print("No power meter detected.\n")

    def setBias(self, volt):
        # Sets bias to specified voltage
        self.daq.AOut(volt, self.Out_channel)
        time.sleep(.1)

    def prepSweep(self):
        print("Preparing for sweep...")
        # Prepares for data collection
        self.Vdata = []
        self.Idata = []
        self.Biasdata = []
        self.Pdata = []
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
            self.Vdata.append(data[self.V_channel])
            self.Idata.append(data[self.I_channel])
            self.Biasdata.append(self.bias)
            if self.pm_is_connected == True:
                self.Pdata.append(self.pm.getData())
                
            # Reformats data
            self.Vdata[index] = self.Vdata[index] * 1000 * self.G_v
            self.Idata[index] = self.Idata[index] * self.G_i
            
            if index%10 == 0:
                print("\nINDEX: ",index)
                print(str('{:.3}'.format(self.Vdata[index])) + ' mV \t{:.3}'.format(str(self.Idata[index])) + ' mA')
                print("BIAS: {:.3}".format(self.bias))
                
            self.bias -= self.step
            index += 1
        
    def endSweep(self):
        self.bias = 0
        self.setBias(self.bias)
        print("\nBias set to zero. \nSweep is over")
       
    def endDAQ(self):
        # Disconnects and releases selected board number
        self.daq.disconnect(self.Boardnum)
        
    def endPM(self):
        # Disconnects power meter
        if self.pm_is_connected == True:
            self.pm.close()
    
    def spreadsheet(self):
        print("\nWriting data to spreadsheet...")
        
        # Creates document for libre office
        out = open("IVData/" + str(self.save_name) + ".xlsx", 'w')

        # Writes data to spreadsheet
        if self.pm_is_connected == True:
            out.write("Voltage (mV) \tCurrent (mA) \tPower (W)\n")
            for i in range(len(Vdata)):
                out.write(str(self.Vdata[i]) + "\t" + str(self.Idata[i]) + "\t" + str(self.Pdata[i]) + "\n")
        else:
            out.write("Voltage (mV) \tCurrent (mA) \n")
            for i in range(len(self.Vdata)):
                out.write(str(self.Vdata[i]) + "\t" + str(self.Idata[i]) + "\n")
        
        out.close()
    
    def plotIV(self):
        # Plot IV curve
        plt.plot(self.Vdata,self.Idata, 'ro-')
        plt.xlabel("Voltage (mV)")
        plt.ylabel("Current (mA)")
        plt.title("IV Sweep - 15mV")
        plt.axis([min(self.Vdata), max(self.Vdata), min(self.Idata), max(self.Idata)])
        plt.show()
        
    def plotPV(self):
        # Plot PV curve
        if self.pm_is_connected == True:
            plt.plot(self.Vdata, self.Pdata, 'bo-' )
            plt.xlabel("Voltage (mV)")
            plt.ylabel("Power (W)")
            plt.title("PV - 15mV")
            plt.axis([min(self.Vdata), max(self.Vdata), min(self.Pdata), max(self.Pdata)])

    
if __name__ == "__main__":
    test = IV()
    test.readFile()
    test.initDAQ()
    test.initPM()
    test.prepSweep()
    test.runSweep()
    test.endSweep()
    test.endDAQ()
    test.endPM()
    test.spreadsheet()
    test.plotIV()
    test.plotPV()
    
    print("\nEnd.")
