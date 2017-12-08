# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 09:43:02 2016

@author: EnriqueAldana
"""

import socket   #for sockets
import sys  #for exit
import json,time,datetime,getopt
import select

host = 'localhost';
port = 8000;
keepLiveTime = 2 # tiem is a seconds
 
class Switch:
    ID = None
    Status = None
    neighborList = {}
    routeTable_Dic ={}
    socket=None
    ControllerHost = ""        
    ControllerPort = 0
    last_Update=time.time()
    kTime=None
         
    def __init__(self, Id):
        self.ID = Id
        
    
    def configuration(self , hostnameP, portNumberP,switchIdP):
        print ("Configuring Controller hostname and Port number to Switch called " , self.ID)
        try:
            
            if hostnameP=='':
                print ("Please enter a valid host name and a well known port (from 0 - 1023)")
                hostnameP = str(input("Host Name: "))
                print("Host name captured is : ", hostnameP)
                
            self.ControllerHost=hostnameP
                
            if portNumberP=='':
                print("Recommended to choose port 8000 as well known port ")
                portNumberP = int(input("Number: "))
                print ("portNumber captured", portNumberP)
                
            self.ControllerPort=int(portNumberP)
            
            if switchIdP=='':
                print("Please enter a valid Id according Graph definition ")
                switchIdP = str(input("Switch Id: "))
                print ("Switch Id captured", switchIdP)
                
            self.ID=switchIdP
            
            print("controller host registered is: ", self.ControllerHost)
            print("controller port registered is: ", self.ControllerPort)
            print("switche Id registered is: ", self.ID)
        
        except Exception as error_controller_config:
            print("There was an error in the configuration of Controller hostname or portNumber.")
            print("Please check the type of the inputs")
            print("Error Controller config:", sys.exc_info()[0], ' Message ', sys.exc_info()[1])
        
        
        print ("Configuration completed to Switch called " , self.ID)
    
    def CREATING_SOCKET (self):   
        try:
            print ("creating socket")
            
            if self.socket== None:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #s  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket=s
            
        except socket.error:
            print ('Failed to create socket')
            sys.exit() 
            
    def CONNECTING_SOCKET (self):
        try:
            if self.socket != None:
                self.socket.connect((self.ControllerHost, self.ControllerPort))
        except socket.error:
            print ('Failed to connecting socket')
        
    def get_ControllerHost(self):
        return self.ControllerHost
    def get_ControllerPort(self):
        return self.ControllerPort
    
           
def REGISTER_REQUEST(switchP):
    
        switchP.last_Update=time.time()
        neighborDic={}
        option = None
        while option != "exit": 
            try :
            # Update 
            
            #Send ID to controller
             print('Sending REGISTER_REQUEST message to %s with %s port for Switch  called %s' % (switchP.ControllerHost, switchP.ControllerPort,switchP.ID))
             msg=None
             msg = '%s,%s'  % ( 'REGISTER_REQUEST', switchP.ID)
             switchP.socket.sendto(msg.encode('utf-8'), (switchP.ControllerHost, switchP.ControllerPort))
            
            except Exception as socket_contacting:
            # receive data from client (data, addr)            
                print("Error contact host ... make sure that Host is running")
                print("Try contact host ... again")
                sys.exit
            
            try :
                print("Waiting for the controller answer")
                try:
                    controllerAnswer = switchP.socket.recvfrom(1024)
                    reply = controllerAnswer[0]
                    addr = controllerAnswer[1] 
                    print ('Controller reply : ', reply.decode("utf-8"), addr)
                    if reply.decode("utf-8") == "REGISTER_RESPONSE":
                        switchP.Status = "Active"
                        print("waiting neighbor list")
                        print("Controller is sending information. Please keep calm")
                        while True:
                            try:
                                    
                                    controllerAnswer = switchP.socket.recvfrom(1024) 
                                    neighbor = controllerAnswer[0].decode('utf-8')
                                    print('Neighbor List received by Controller is ' , neighbor)
                                    neighborDic=json.loads(neighbor)
                                    switchP.neighborList=neighborDic
                                    for k in neighborDic.keys():        
                                            print(k)
                                            print(neighborDic[k])
                                    option = "exit"
                            except socket.timeout:
                                print("Controller is not sending more info. socket time out exception")
                                reply = None                            
                                option = "exit"
                                break
                            except Exception:
                                print("Error trying to receive neighbor list: ", sys.exc_info()[0])
                                break
                    else:
                        print(reply)
                except socket.timeout:
                    print("time for request response was exceeded")
                    sys.exit
                
            except Exception as socket_sending:
                # receive data from client (data, addr)
                print("Error sending")
                #print ('Error Code  : ', str(socket_sending[0]), ' Message ', socket_sending[1])
                sys.exit
        

def TOPOLOGY_UPDATE(switchP): 
    #Get neighbor list
        switchP.last_Update=time.time()
        neighborDic={}
        option = None
        while option != "exit": 
            switchP.last_Update=time.time()
            try :
            #Send ID to controller
             print('Sending TOPOLOGY_UPDATE message to %s with %s port for Switch  called %s' % (switchP.ControllerHost, switchP.ControllerPort,switchP.ID))
             msg=None
             msg = '%s,%s'  % ( 'TOPOLOGY_UPDATE', switchP.ID)
             switchP.socket.sendto(msg.encode('utf-8'), (switchP.ControllerHost, switchP.ControllerPort))
             print("Already sent")
            
            except Exception as socket_contacting:
            # receive data from client (data, addr)            
                print("Error contact host to TOPOLOGY_UDDATE request ")
                
                sys.exit
            
            try :
                print("Waiting for the controller answer to TOPOLOGY_UPDATE request")
                try:
                    
                    controllerAnswer = switchP.socket.recvfrom(1024)
                    reply = controllerAnswer[0]
                    addr = controllerAnswer[1] 
                    print ('Controller reply : ', reply.decode("utf-8"), addr)
                    
                    if reply.decode("utf-8") == "TOPOLOGY_UPDATE":
                        switchP.Status = "Active"
                        print("waiting neighbor list")
                        print("Controller is sending information. Please keep calm")
                        while True:
                            try:
                                controllerAnswer = switchP.socket.recvfrom(1024) 
                                neighbor = controllerAnswer[0].decode('utf-8')
                                print('Neighbor List in TOPOLOGY_UPDATE request has been received  ' , neighbor)
                                neighborDic=json.loads(neighbor)
                                switchP.neighborList=neighborDic
                                for k in neighborDic.keys():        
                                        print(k)
                                        print(neighborDic[k])
                                option = "exit"
                            except socket.timeout:
                                print("Controller is not sending more info")
                                reply = None                            
                                option = "exit"
                                break
                            except Exception:
                                print("Error trying to receive neighbor list: ", sys.exc_info()[0])
                                break
                    else:
                        print('Controller has sent a message different that TOPOLOGY_UPDATE ' ,reply)
                except socket.timeout:
                    print("time for request response was exceeded")
                    sys.exit
                
            except Exception as socket_sending:
                # receive data from client (data, addr)
                print("Error sending")
                #print ('Error Code  : ', str(socket_sending[0]), ' Message ', socket_sending[1])
                sys.exit
        
def ROUTE_UPDATE(switchP): 
    #Get neighbor list
        switchP.last_Update=time.time()
        option = 'continuar'
        while option != "exit": 
            switchP.last_Update=time.time()
            try :
            #Send ID to controller
             print('Sending ROUTE_UPDATE message to %s with %s port for Switch  called %s' % (switchP.ControllerHost, switchP.ControllerPort,switchP.ID))
             msg=None
             msg = '%s,%s'  % ( 'ROUTE_UPDATE', switchP.ID)
             switchP.socket.sendto(msg.encode('utf-8'), (switchP.ControllerHost, switchP.ControllerPort))
             print("Already sent ROUTE_UPDATE request")
            
            except Exception as socket_contacting:
            # receive data from client (data, addr)            
                print("Error contact host to ROUTE_UPDATE request ")
                
                sys.exit
            
            try :
                print("Waiting for the controller answer to ROUTE_UPDATE request")
                try:
                    
                    controllerAnswer = switchP.socket.recvfrom(1024)
                    reply = controllerAnswer[0]
                    addr = controllerAnswer[1] 
                    print ('Controller reply : ', reply.decode("utf-8"), addr)
                    
                    if reply.decode("utf-8") == "ROUTE_UPDATE":
                        switchP.Status = "Active"
                        print("Waiting Route  table")
                        print("Controller is sending information. Please keep calm")
                        while True:
                            try:
                                controllerAnswer = switchP.socket.recvfrom(1024) 
                                routeTable = controllerAnswer[0].decode('utf-8')
                                print('Route table in ROUTE_UPDATE request has been received  ' , routeTable)
                                routeTableDic=json.loads(routeTable)
                                switchP.routeTable_Dic=routeTableDic
                                for k in routeTableDic.keys():        
                                        print('Target node %s' % k)
                                        print('Route Table' % routeTableDic[k])
                                print('The routing table for the node %s is: ' % switchP.ID)
                                print('Destination | Next hop')
                                
                                for k in routeTableDic.keys(): 
                                    #print('The Node called %s has value %s' % (k,dictionary[k]))
                                    cadenaRuta={}
                                    cadenaRuta=routeTableDic[k]
                                    #print('cadenaRuta ' , cadenaRuta)
                                    #print('Longitud cadenaRuta' , len(cadenaRuta))
#                                    for i in range(0, len(cadenaRuta)):
                                    if (len(cadenaRuta)==1):
                                        print('to:  node %s  | node neighbord is %s ' % (k,cadenaRuta[0]))
                                       
                                    else:
                                        print('to:  node %s  | node neighbord is %s ' % (k,cadenaRuta[len(cadenaRuta)-2]))
                                            
                                            
                                option = "exit"
                            except socket.timeout:
                                print("Controller is not sending more info for route table")
                                reply = None                            
                                option = "exit"
                                break
                            except Exception:
                                print("Error trying to receive neighbor list: ", sys.exc_info()[0])
                                break
                    else:
                        print('Controller has sent a message different that TOPOLOGY_UPDATE ' ,reply)
                except socket.timeout:
                    print("time for request response was exceeded")
                    sys.exit
                
            except Exception as socket_sending:
                # receive data from client (data, addr)
                print("Error sending")
                #print ('Error Code  : ', str(socket_sending[0]), ' Message ', socket_sending[1])
                sys.exit

        
def ROUTE_UPDATE_received(sP):
    
            sP.last_Update=time.time()
            option = None
            while option != "exit":      
                    print("Waiting for the controller answer to ROUTE_UPDATE request")
                    print("waiting route table")
                    try:
                            
                            msg=None
                            msg = '%s,%s'  % ( 'ROUTE_UPDATE_PUSH', sP.ID)
                            sP.socket.sendto(msg.encode('utf-8'), (sP.ControllerHost, sP.ControllerPort))
                            
                            controllerAnswer = sP.socket.recvfrom(1024)
                            ans=controllerAnswer[0]
                            jsonString = ans.decode('utf-8')
                            # print('Route table decode %s' % jsonString)
                            cadena=jsonString
                            dictionary={}
                            dictionary= json.loads(cadena)
                            #print('Route String received ' , cadena)
                            #print('Route received into dictionary' , dictionary)
                            #print('Nodes in Route', dictionary.keys())
                            print('The routing table for the node %s is: ' % sP.ID)
                            print('Destination | Next hop')
                                
                            for k in dictionary.keys(): 
                                #print('The Node called %s has value %s' % (k,dictionary[k]))
                                cadenaRuta={}
                                cadenaRuta=dictionary[k]
                                #print('cadenaRuta ' , cadenaRuta)
                                #print('Longitud cadenaRuta' , len(cadenaRuta))
                                for i in range(0, len(cadenaRuta)):
                                    if k == cadenaRuta[i] and i+1 != len(cadenaRuta):
                                        neighbordIndex=i+1
                                        #print('Elem %s es %s' % (i,cadenaRuta[i]))
                                        #print ('The neighbort is ' , cadenaRuta[neighbordIndex])
                                        print('to:  node %s  | node neighbord is %s ' % (k,cadenaRuta[neighbordIndex]))
                                        
                            
                            sP.routeTable_Dic= dictionary
                            option = "exit"                                          
                    except socket.timeout:
                        print("Controller is not sending more info for route table")                           
                        option = "exit"
                        break
                    except Exception:
                        print("Error trying to receive route table: ", sys.exc_info()[0])
                        break
                        
                    
                

def timeStampRightNow():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st
            
def request_TOPOLOGY_ROUTE_UPDATE(timeP,switchP):
    
            timePeriod = timeP - switchP.last_Update
            # print('Expiration time %f of %f ' % (timePeriod,switchP.kTime))
            if timePeriod > switchP.kTime:
                print(' %s Switch : %s has sent topology update request' % (timeStampRightNow(),switchP.ID))
                TOPOLOGY_UPDATE(switchP)
                ROUTE_UPDATE(switchP)

               
        
def switchRun(hostnameP,portnumberP,switchIdP,KTimeP):

        print()
        print ('Switch called %s  is listening in %s with port %s' % (switchIdP,hostnameP,portnumberP))
        print ('Press Enter key to End program, ')
        
        switch = Switch(switchIdP)
        switch.configuration(hostnameP,portnumberP,switchIdP)
        socket.setdefaulttimeout(int(10))
        
        try:
            switch.CREATING_SOCKET()
            # switch.CONNECTING_SOCKET()
    
        except Exception as socket_creation:
            print("Error socket creation")
            #print ('Error Code  : ', str(socket_creation[0]), ' Message ', socket_creation[1]) 
              
        input = [switch.socket,sys.stdin] 
        running = 1
        ktime= float(KTimeP)
        switch.last_Update=time.time()
        switch.kTime=ktime
        
        # Request to Controller REGISTER_REQUEST
        REGISTER_REQUEST(switch)
        
        while running:
            
            inputready,outputready,exceptready = select.select(input,[],[],0.001) 
            
            for s in inputready: 
        
                if s == switch.socket:   # (1) We have received a request and go to handle all others sockets section below (2)
                     print('Not implemented yet')
#                    # handle the server socket 
#                    try:
#                        print("Switch is expecting to receive info from Controller")                     
#                        d = switch.socket.recvfrom(1024)
#                        print("Data from Controller received")
#                        data = d[0].decode('utf-8')
#                        addr = d[1]
#                        print ("Received message: ", data,"from", addrController)
#                        print('Message ' , data)
#                        print('Address' , addr)
#                        
#                        order=''
#                        if data:
#                            msgSplited  = data.split(',')
#                            order       = msgSplited[0]
#                            swId        = msgSplited[1]
#                            address     = addr[1]
#                            iP          = addr[0]
#                            print('Order is %s' % order )
#                            print('Switch Id is %s' % swId )
#                            
#                            if order == 'ROUTE_UPDATE_PUSH':
#                                   print ('Receiving ROUTE_UPDATE from Controller ') 
#                                   ROUTE_UPDATE_received(switch)
#                                   
#                        
#                        else:
#                            print('None data')
#                        
#                            
#                        
#                    except Exception as error_receiving_controller:
#                        print("Error receiving:", sys.exc_info()[0], sys.exc_info()[1])
                         
                elif s == sys.stdin: 
                    # handle standard input 
                    ketEntered = sys.stdin.readline()
                    running = 0
               
                else:
                    print('handle all other sockets')
                   
                       
            # End for
            # validate LIVE nodes
            #print('time' , time.time())
            
            request_TOPOLOGY_ROUTE_UPDATE(time.time(),switch)
            
                
            # else UPDATE Topology
                        
        # End while running
        print('Switch program has terminated')
        switch.socket.close()   
            

def main(argv):
   hostnameParameter = None
   hostportParameter = None 
   idParameter=None
   arguments=0
   KTime=None
   try:
      #opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
      opts, args = getopt.getopt(argv,"h:n:p:i:k:",["hostnameParameter=","hostportParameter=","idParameter=","KTime="])
      arguments=args
   except getopt.GetoptError:
       print ('Switcher.py -n <controller hostname>  -p <controller port> -i <Id Switcher> -k <refress time to KEEP LIVE' )
       #print( 'Controller.py -i <inputfile> -o <outputfile>')
       sys.exit(2)
   for opt, arg in opts:
       if opt == '-h':   # Requested Help to use it
         print ('Switch.py <controller hostname>  <controller port> <switch Id>')
         sys.exit()
      
       elif opt in ("-n", "--hostnameParameter"):
         hostnameParameter = arg
         
       elif opt in ("-p", "--hostportParameter"):
         hostportParameter = arg
         
       elif opt in ("-i", "--idParameter"):
         idParameter = arg
        
       elif opt in ("-k", "--KTime"):
         KTime = arg 
         
   if len(arguments)== 0:
          if hostnameParameter==None:
              hostnameParameter = 'localhost'
          if hostportParameter==None:
              hostportParameter= 8000
          if idParameter==None:
              idParameter=''
          if KTime==None:
              KTime=float(5)    
          print('Switch program has been started ')      
          print ('Host name is ', hostnameParameter)
          print ('Port number is ', hostportParameter)
          print ('Switch Id is ' ,idParameter)
          print ('K time for refresh KEEP ALIVE is : %s seconds' % KTime)
          
          switchRun(hostnameParameter,hostportParameter,idParameter,KTime)
          
          
   
   
if __name__ == "__main__":
   main(sys.argv[1:])  