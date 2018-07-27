from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType, DigitalDirection, DigitalPortIoType
import time
import os

bit_number = 7     # Control bit is at A7
ambload = 0        
coldload = 1
direction = DigitalDirection.OUTPUT
interface_type = InterfaceType.USB


devices = get_daq_device_inventory(interface_type)
if len(devices) == 0:
    raise Exception('Error: No DAQ devices found')

print('Found', len(devices), 'DAQ device(s):')
for i in range(len(devices)):
    print('  ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

# Create the DAQ device object associated with the specified descriptor index.
daq_device = DaqDevice(devices[0])

# Get the DioDevice object and verify that it is valid.
dio_device = daq_device.get_dio_device()

# Establish a connection to the DAQ device.
descriptor = daq_device.get_descriptor()
print('\nConnecting to', descriptor.dev_string, '- please wait...')
daq_device.connect()
os.system("clear")

# Get the port types for the device(AUXPORT, FIRSTPORTA, ...)
dio_info = dio_device.get_info()
port_types = dio_info.get_port_types()
port_to_write = port_types[0]

# Configure port
dio_device.d_config_port(port_to_write, DigitalDirection.OUTPUT)

# Writes output for bit
dio_device.d_bit_out(port_to_write, bit_number, coldload)

"""
t0 = time.time()
for n in range(0,10,1):
    dio_device.d_bit_out(port_to_write, bit_number, ambload)
    time.sleep(1)
    dio_device.d_bit_out(port_to_write, bit_number, coldload)
    time.sleep(1)
    
    print(n, time.time()-t0)

t1 = time.time()

print(t1-t0)
"""
# Control load mover via input
while True:
    move = input("Move load [up, down, or end] : ")
    if move == "up":
        dio_device.d_bit_out(port_to_write, bit_number, ambload)
        print("\tMoving up\n")
    elif move == "down":
        dio_device.d_bit_out(port_to_write, bit_number, coldload)
        print("\tMoving down\n")
    elif move == "end":
        print("\tEnd program\n")
        break
    else:
        print("\tEnd program\n")
        break
    
daq_device.disconnect()
daq_device.release()
os.system("clear")

