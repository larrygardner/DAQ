import DAQ
import time
import os

class LoadMover:
    def __init__(self):
        self.board_number = 0
        self.bit_number = 7     # Control bit is at A7
        self.ambload = 0        
        self.coldload = 1

    def initDAQ(self):
        # Connects DAQ
        self.daq = DAQ.DAQ()
        self.daq.listDevices()
        self.daq.connect(self.board_number)
        self.daq.configDOut()
    
    def move(self):
        os.system("clear")
        # Control load mover via input
        while True:
            move = input("\nMove load [up, down, or end] : ")
            if move == "up":
                self.daq.DOut(self.ambload, self.bit_number)
                print("\tMoving up")
            elif move == "down":
                self.daq.DOut(self.coldload, self.bit_number)
                print("\tMoving down")
            elif move == "end":
                print("\tEnd program")
                break
            else:
                print("\tEnd program")
                break

    def move_time(self, interval = 1, length = 10):
        os.system("clear")
        t0 = time.time()
        for n in range(0, length, interval):
            self.daq.DOut(self.ambload, self.bit_number)
            print("\tMoving up\n")
            time.sleep(1)
            self.daq.DOut(self.coldload, self.bit_number)
            print("\tMoving down\n")
            time.sleep(1)

    def end(self):
        # Ends program and disconnects devices
        self.daq.disconnect()
    
    
if __name__ == "__main__":
    lm = LoadMover()
    lm.initDAQ()
    lm.move_time(1,10)
    lm.move()
    lm.end()
    