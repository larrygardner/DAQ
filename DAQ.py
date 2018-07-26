##################################################
#                                                #
# Class for operating DAQ devices                #
#                                                #
# Larry Gardner, July 2018                       #         
#                                                #
##################################################

from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType, AiInputMode, AInFlag

class DAQ:
    def __init__(self):
        self.device = None
        
    def connect(self):
        # Connects to DAQ device     
        try:
            self.device = get_daq_device_inventory(InterfaceType.USB)
            self.number_of_devices = len(self.device)
            if self.number_of_devices == 0:
                raise Exception('Error: No DAQ devices found')
            print("\nFound " + str(self.number_of_devices) + " DAQ device(s):")
            for i in range(self.number_of_devices):
                print("    ", self.device[i].product_name, " (", self.device[i].unique_id, ")", sep="")
            # Creates DAQ device object
            self.daq_device = DaqDevice(self.device[0])
            self.ai_device = self.daq_device.get_ai_device()
            # Connect to DAQ device
            descriptor = self.daq_device.get_descriptor()
            self.daq_device.connect()
            print("\nConnected to ", descriptor.dev_string)
        except (KeyboardInterrupt, ValueError):
            print("Could not connect DAQ device.")
            
    def disconnect(self):
        # Disconnects DAQ device
        if self.daq_device:
            if self.daq_device.is_connected():
                self.daq_device.disconnect()
                print("\nDAQ device", self.device[0].product_name, "is disconnected.")
            print("DAQ device", self.device[0].product_name, "is released.")
            self.daq_device.release()