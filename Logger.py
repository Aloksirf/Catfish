import sqlite3
import random
import os
import serial
from datetime import datetime
import time
import statistics

from Connect import Connect
from Maths import Maths
import Client


class Logger:
    #init initielises the logger
    def __init__(self):
        #Create a dictunary where the key
        self.data_dict = {}
        #The class Connect cheks the connection between arduino and raspberry. Chek the class for more info
        self.connect = Connect()
        #Connecting to the local database and setting a cusosr
        conn = sqlite3.connect('Local.db')
        cursor = conn.cursor()
        
        #Sets the catID to the max value in the database
        cursor.execute("SELECT MAX(CatID) FROM CatData")
        temp = cursor.fetchone()[0]
        self.catID = 0
        if(temp != None):
            self.catID = int(temp)
         #Sets the fishID to the max value in the database
        cursor.execute("SELECT MAX(FishID) FROM FishData")
        temp = cursor.fetchone()[0]
        self.fishID = 0
        if(temp != None):
            self.fishID = int(temp)
            
        #Sets the waypointID to the max value in the database
        cursor.execute("SELECT MAX(waypiontID) FROM Waypoint")
        temp = cursor.fetchone()[0]
        self.waypointID = 0
        if(temp != None):
            self.waypointID = int(temp)
        
        #Set a new mission to the value
        cursor.execute("SELECT MAX(missionID) FROM Waypoint")
        temp = cursor.fetchone()[0]
        self.missionNr = 0
        if(temp != None):
            self.missionNr = int(temp)+1
        conn.close()
    
    #Getts the data from the raspberry and stores it in the dictonary. It will take some samples of data and calculate the
    #Returns true if succesfully connected and false if not
    #If no connection after 9 trys (1min) then it will return false
    def collect_data(self):
        catSer = None  #Serial for cat comunication
        collected = False
        j = 0
        while(not collected):    
            while(catSer == None and j < 9):
                catSer = self.connect.getCat()
                #here we move the servo to get connection.
                j = j+1
            if(j >= 9):
                return False
            #List of all the inputts
            tempCats = []
            Phs = []
            turbidityCats = []
            TDSs = []
            voltConds = []
            ecConds = []
            dissolvedOxygenCats = []
            #Collecting the data from the arduino
            try:
                for x in range(6):
                    tempCats.append(self.collect_loop('1', catSer))
                    Phs.append(self.collect_loop('2', catSer))
                    turbidityCats.append(self.collect_loop('3', catSer))
                    TDSs.append(self.collect_loop('4', catSer))
                    voltConds.append(self.collect_loop('5', catSer))
                    ecConds.append(self.get_from_arduino(catSer))
                    dissolvedOxygenCats.append(self.collect_loop('6', catSer))
                collected = True
            #if connection is broken start over
            except:
                tempCats.clear()
                Phs.clear()
                turbidityCats.clear()
                TDSs.clear()
                voltConds.clear()
                ecConds.clear()
                dissolvedOxygenCats.clear()
                self.connect.disConnect()
                catSer = None
                collected = False
            
        #Calculate the mode/mean for the values
        tempCat = Maths.modeMean(tempCats)
        Ph = Maths.modeMean(Phs)
        turbidityCat = Maths.modeMean(turbidityCats)
        TDS = Maths.modeMean(TDSs)
        voltCond = Maths.modeMean(voltConds)
        ecCond = Maths.modeMean(ecConds)
        dissolvedOxygenCat = Maths.modeMean(dissolvedOxygenCats)
        
        catID = self.catID+1
        self.data_dict['CatData'] = [catID,tempCat,Ph,turbidityCat,TDS,voltCond,ecCond,dissolvedOxygenCat]
        
        fishSer = None #Serial comunication with fish
        while(fishSer == None):
            fishSer = self.connect.getFish()
        #Lists of all inputs
        tempFishs = []
        dissolvedOxygenFishs = []
        turbidityFishs = []
        #collect the data
        for x in range(6):
            tempFishs.append(self.collect_loop('1', fishSer))
            dissolvedOxygenFishs.append(self.collect_loop('2', fishSer))
            turbidityFishs.append(self.collect_loop('3',fishSer))
        #get the mode/mean from the data
        tempFish = Maths.modeMean(tempFishs)
        dissolvedOxygenFish = Maths.modeMean(dissolvedOxygenFishs)
        turbidityFish = Maths.modeMean(turbidityFishs) 
        #Insert the answer in the dictonary
        fishID = self.fishID+1
        self.data_dict['FishData'] = [fishID,tempFish,dissolvedOxygenFish,turbidityFish]
        
        #here we need to get the cordinates and the time from the pixhawk.
        cordinates = random.randint(0,100)
        time = datetime.now()
        #Insert the answer in the dictonary
        waypointID = self.waypointID+1
        self.data_dict['Waypoint'] = [waypointID,time,cordinates,catID,fishID,0,self.missionNr]
        return True
    
    #Checks if we do not get any values or it times out
    def collect_loop(self, nr, ser):
        ret = -1;
        t = time.time()
        while(ret == -1 and time.time()-t < 10):
            self.write_to_arduino(nr, ser)
            ret = self.get_from_arduino(ser)
        return ret
    
    #Assume that ser is already checked
    def get_from_arduino(self,ser):
        t = time.time();
        while(ser.in_waiting <= 0):
            time.sleep(0.01)
            if(time.time()-t > 3):
                return -1
        if(ser.in_waiting > 0):
            ret = float(ser.readline())
            return ret
    
    #Assume that ser is already checked
    def write_to_arduino(self,send,ser):
        ser.write(bytes(send.encode()))
    
    #Print the data in the dictonarys
    def print_data(self):
        print ("Catvalues = temp: {1:f}, PH: {2:f},turb: {3:f},TDS : {4:f}, Vcond: {5:f}, ecCond {6:f}, DisOxy: {7:f} ".format(*self.data_dict['CatData']))
        print ("Fishvalues = temp: {1:f}, disOxy: {2:f}, turb: {3:f}".format(*self.data_dict['FishData']))
        print ("Time: {1:%Y-%m-%d} Cordinates: {2:f}, catID: {3:d}, fishID: {4:d}, sent: {5,d}, missionNr: {6:d}".format(*self.data_dict['Waypoint']))
    
    #putts the data in the local database
    def logg_data(self):
        #connect to the database
        conn = sqlite3.connect('Local.db')
        cursor = conn.cursor()
        
        for table, data in self.data_dict.items():
            if(table != "Waypoint"):
                cnt = len(data)-1
                params = '?' + ',?'*cnt
                cursor.execute(f"INSERT INTO {table} VALUES("+params+")",data)
        self.catID = self.catID + 1
        self.fishID = self.fishID + 1
        cursor.execute(f"INSERT INTO {table} VALUES("+'?,?,?,?,?,?,?'+")",data)
        conn.commit()
        conn.close()
        

def main():
    logg = Logger()
    success = logg.collect_data()
    if(success):
        logg.logg_data()
    else:
        print("fail")
