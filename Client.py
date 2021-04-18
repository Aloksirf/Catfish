import socket
import sqlite3
import json

#returns a list of all the rows that are not sent to the main database
def getNonSent():
    conn = sqlite3.connect('Local.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM NonSent")
    #waypointID,time, dordinates, missionID, CatID, CatData.temperature, PH, Cat.turbidity, TDS, Conductivity(V),
    #Conductivity(EC), DissolvedOxygen, FishID, Fish.temperature Fish.disolvedOxyen, Fish turbidity
    temp = cursor.fetchall()
    conn.close()
    return temp    

#connecting to the server
def client_connect():
    host = '192.168.0.36'
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server
    return client_socket

def client_program(client_socket, d):
    conn = sqlite3.connect('Local.db')
    cursor = conn.cursor()
    json_string = json.dumps(str(d))
    #while message.lower().strip() != 'bye':
    client_socket.send(json_string.encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response
    #if we recive a 1 the data has been stored
    if(data == '1'):
        stri = "UPDATE Waypoint SET sent = 1 WHERE waypiontID = "+str(d[0]);
        cursor.execute(stri)
        conn.commit()
    conn.close()

#the main for the code. When this runns it will try to send the data to the main database.
#It returns 1 if it has no more data to send and 0 if there might be more data to send
def sendData():
    tosend = getNonSent()
    if tosend:
        client_socket = client_connect()
        for x in tosend:
            client_program(client_socket,x)
        client_socket.close()
        return 0
    return 1

if __name__ == '__main__':
    tosend = getNonSent()
    if tosend:
        client_socket = client_connect()
        for x in tosend:
            client_program(client_socket,x)
        client_socket.close()  
    
