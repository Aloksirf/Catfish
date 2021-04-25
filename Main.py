from Logger import Logger
import Client
import time

def main():
    #The mission starts/inisialises
    logg = Logger() #Create a new instans of logger. Creates a new missionNr in the database
    missionOnGoing = True #It will be in a while loop until the mission is starting
    while(missionOnGoing):
        #At the same time as the catfish is sailing to the next waypoint it will
        #try to send data that is not sent to the server
        Client.sendData()
        
        #When the catfish has gotten to the waypoint
        atWaypoint = True #check if catfish arrived at waypoint 
        if(atWaypoint):
            #take down the fish
            success = logg.collect_data() #get the data from the cat and fish
            if(success):
                logg.logg_data() #if the data is collected logg the data
            else:
                print("Error") #if the datacollection whent wrong go to the next waypoint
            #drag the fish upp to the cat again
            #tell the pixhawk that we are done and send it to the next waypoint
        
        #when we are done with a mission set the missionOnGoing to false
                print("reset")
        time.sleep(1) #set a time so the pi does not work to hard
main()

