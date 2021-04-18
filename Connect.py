import  serial
import time

class Connect:

    def __init__(self):
        self.con = False
        self.case = 0
    
    #connecting to the arduinos   
    def connect(self):
        try:
            self.ser0 = serial.Serial('/dev/ttyACM0',9600)
            self.ser1 = serial.Serial('/dev/ttyACM1',9600)
            self.con = True
            print('connected')
        except:
            self.con = False
            print('no connection')
        time.sleep(2)
    #disconnecting the chanels that where used
    def disConnect(self):
        self.ser0.close()
        self.ser1.close()
        self.case = 0
        time.sleep(2)
        print('disconnect')
    
#case = 0, not known
#case = 1, ser0 = cat, ser1 = fish
#case = 2, ser1 = cat, ser0 = fish
#This code tries to connect for 7 seconds, if it succeeds to connect, it will return true. If it timeouts, it will return false.
#The code sends a H for hello to the arduino. It will andwser with ither a C for Cat og F for Fish
    def loop(self):
        self.connect()
        t = time.time();
        while(time.time() - t < 7):
            try:
                if(self.con):
                    self.ser0.write((bytes)('H'.encode()))
                    while(self.ser0.in_waiting <= 0):
                        time.sleep(0.5)
                    if(self.ser0.in_waiting > 0):
                        line1 = self.ser0.readline()
                    time.sleep(1)
                    self.ser1.write((bytes)('H'.encode()))
                    while(self.ser1.in_waiting <= 0):
                        time.sleep(0.1)
                    if(self.ser1.in_waiting > 0):
                        line2 = self.ser1.readline()
                    time.sleep(1)
                    #Makes sure that both have connection
                    if(line1 == b'C\r\n' and line2 == b'F\r\n'):
                        self.case = 1
                        return True 
                    elif(line1 == b'F\r\n' and line2 == b'C\r\n'):
                        self.case = 2
                        return True    
                else:
                    self.connect()
            except:
                self.disConnect() 
                self.connect()
        #wad ska vi göra om det blir False
        return False
               
    def getCase(self):
        return self.case
    
    #Returns null if it doesn't work, after it tries to connect. (Null means that you have to move the servo.)
    def getCat(self):
        self.loop()
        if(self.case != 0 and self.con != False):
            if(self.case == 1):
                return self.ser0
            elif(self.case == 2):
                return self.ser1
        else:
            return None
    
    #Returns null if it doesn't work, after it tries to connect. (Null means that you have to move the servo.)
    def getFish(self):
        self.loop()
        if(self.case != 0 and self.con != False):
            if(self.case == 1):
                return self.ser1
            elif(self.case == 2):
                return self.ser0
        else:
            return None
               