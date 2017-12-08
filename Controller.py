# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 15:36:08 2016

@author: EnriqueAldana

V6 Add 
config.txt
"""
import socket
import sys
import fileinput
import heapq
import json
import time
import getopt
import select
import datetime

hostname = '';
portNumber = 0;
keepLiveTime = 2 # time is a seconds
livesNodes_Dic={}
nodesNumber=0
configPathFile='config.txt'
backlog = 5
size = 1024

class Controller():
    ControllerHost = ""
    ControllerPort = None

    def configuration(self, hostname, portNumber):
        print ("Configuring Controller hostname and Port number")
        self.ControllerHost = hostname        
        self.ControllerPort = int(portNumber)
        print ("Configuration completed")
    
    def socketCreation(self):
        print("Creating the socket")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket created", sock)
        return sock
    
    def get_ControllerHost(self):
        return self.ControllerHost
    def get_ControllerPort(self):
        return self.ControllerPort

       
class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxsize 
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None
        # V2 
        self.available ='No'
        self.iPsocketAddress=None
        self.lastTime= time.time()
      
        
    def set_lastTime(self,tsP):
        self.lastTime=tsP
        
    def get_socketAddress(self):
        return self.iPsocketAddress
        
    def set_socketAddress(self,iPsocketAddressP):
        self.iPsocketAddress= iPsocketAddressP
        
        
    def get_lastTime(self):
        return self.lastTime 
        
    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight
        
    def rem_neighbor(self, neighbor):
        del self.adjacent[neighbor]

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def set_distance(self, dist):
        self.distance = dist

    def get_distance(self):
        return self.distance

    def set_previous(self, prev):
        self.previous = prev

    def set_visited(self):
        self.visited = True
        
    def set_available(self):
        self.available= 'Yes'
     
    def set_unavailable(self):
        self.available= 'No'
        
    def get_available(self):
        return self.available
        
    def __lt__(self, other):  # it is mandatory to Python 3 when you need became Orderable the Object instanted of your Class
         return (self.distance < other.distance)

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])
            
class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0
        self.startFirstTime='Yes'
        self.areAllNodesRegistered=False
        
        
    def __iter__(self):
        return iter(self.vert_dict.values())    

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        new_vertex.set_unavailable()
        self.vert_dict[node] = new_vertex
        return new_vertex
        
    def rem_vertex(self, nodeName):
        if nodeName in self.vert_dict:
            self.num_vertices = self.num_vertices - 1
            v= self.get_vertex(nodeName)
            for w in v.get_connections():  # for each Vertex get array of the neighbor data
                vid = v.get_id()
                wid = w.get_id()
                print ('Delete Node %s  neighbor %s  with %s'  % ( vid, wid, v.get_weight(w)) )
                self.rem_edge(vid,wid)
          
            del self.vert_dict[nodeName]
            
    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
            #here add to vert_dict array frm and to vertex if not were included. JEAS 
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)
            # Here add to frm and to vertex item the neighbor and cost
            # thats mean : for each vertex has a adjacent array with neighbor data
        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)
        
    def rem_edge(self,frm,to):
         self.vert_dict[to].rem_neighbor(self.vert_dict[frm])
        
    def get_vertices(self):
        return self.vert_dict.keys()

    def set_previous(self, current):
        self.previous = current

    def get_previous(self, current):
        return self.previous
        
    

    def dijkstra(self, aGraph, start):
        print ('Dijkstras shortest path computing process')
        # Set the initial node as current. Create a list of the unvisited nodes called the unvisited list
        # consisting of all the nodes. We do it using tuple pair, (distance, v)
        if start != None:
                # Set the distance for the start node to zero 
                start.set_distance(0)
            
                # Put tuple pair into the priority queue
                unvisited_queue = [(v.get_distance(),v) for v in aGraph]
                heapq.heapify(unvisited_queue)
            
                # Strategy : For the current node, consider all of its unvisited neighbors and calculate their tentative distances.
                # Compare the newly calculated tentative distance to the current assigned value and assign the smaller one. 
                # For example, if the current node A is marked with a distance of 6, and the edge connecting it with a neighbor B has length 2, 
                # then the distance to B (through A) will be 6 + 2 = 8. If B was previously marked with a distance greater than 8 then change it to 8. 
                # Otherwise, keep the current value.
            
                while len(unvisited_queue):
                    # When we are done considering all of the neighbors of the current node, 
                    # mark the current node as visited and remove it from the unvisited set.
                    # Pops a vertex with the smallest distance .
                
                    # heapq.heappop(heap) command  Pop and return the smallest item from the heap, maintaining the heap invariant. 
                    # If the heap is empty, IndexError is raised.
                    # reference is in https://docs.python.org/3.2/library/heapq.html
                
                    uv = heapq.heappop(unvisited_queue)   # get a Vertex with smallest adjacent value that is a distance attribute
                    current = uv[1]    
                    current.set_visited()
            
                    #for next in v.adjacent:
                    # for each vertex has a adjacent array with neighbor data
                    for next in current.adjacent:
                        # if visited, skip
                        if next.visited:
                            continue
                        new_dist = current.get_distance() + current.get_weight(next)
                        
                        if new_dist < next.get_distance():
                            next.set_distance(new_dist)
                            next.set_previous(current)
                            print ('updated : current = %s next = %s new_dist = %s' \
                                    %(current.get_id(), next.get_id(), next.get_distance())
                                )
                        else:
                            print ( 'not updated : current = %s next = %s new_dist = %s' \
                                    %(current.get_id(), next.get_id(), next.get_distance())
                                    )
                    # Rebuild heap
                    # 1. Pop every item
                    while len(unvisited_queue):
                        heapq.heappop(unvisited_queue)
                    # 2. Put all vertices not visited into the queue
                    unvisited_queue = [(v.get_distance(),v) for v in aGraph if not v.visited]
                    heapq.heapify(unvisited_queue)
        else:
            print ('Initial Node is None')
    # recursive function that get previous nodes fromtarget node       
    def getShortPathForTargetNode(self,targetNode,shortPath):
            if targetNode.previous:
                    shortPath.append(targetNode.previous.get_id())
                    self.getShortPathForTargetNode(targetNode.previous,shortPath)
            return        
    def getShortPathFrom(self,initialNodeName):
        self.dijkstra(self, self.get_vertex(initialNodeName)) # Node a is starting path.
        shortpathresults = {}
        for v in self: # Vertex list in Graph() object
              #print ('Short path from %s Node to %s' % (initialNodeName , v.get_id()))
              targetNode = self.get_vertex(v.get_id())
              shortPath=[targetNode.get_id()]
              self.getShortPathForTargetNode(targetNode,shortPath)
              shortpathresults[v.get_id()]=shortPath
              #print ('The short path is : %s'  % shortPath[::-1])
        print ( )
        print ('Dijkstras shortest path computing process Results')
        print ( )
        for targetNodo in shortpathresults:
                print ('From node called %s to %s the short rute is %s' %  (initialNodeName,targetNodo, shortpathresults[targetNodo][::-1]))
                
        return shortpathresults   

    def printGraph(self):
             print ('Graph data:')
             for nodoName in sorted(self.vert_dict.keys()): # Vertex list in Graph() object
                v = self.get_vertex(nodoName)
                print ('Node %s  is available : %s' % (nodoName,v.get_available()) )
                print ('Neighbors ')
                for w in v.get_connections():  # for each Vertex get array of the neighbor data
                    vid = v.get_id()
                    wid = w.get_id()
                    print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w))
                        )

def loadDinamicGraphWithAvailablesNodes(sourceGraph,targetGraph):
# Load a Dinamic Graph Object Just with availables nodes from Initial Graph called g
    unavailable_queue = {}
    available_queue = {}
   
    for v in sourceGraph: # Vertex list in Graph() object
        if v.available=='Yes' :
            available_queue[v.get_id()]=v.get_id()
        else:
            unavailable_queue[v.get_id()]=v.get_id()
    #print ('lista de disponibles %s' %  available_queue)
    #print ('lista de NO disponibles %s' %  unavailable_queue)
    
    for v in sourceGraph: # Vertex list in Graph() object 
        if v.available=='Yes' :       
            print ()
            print('Loading availables nodes to Dinamic graph object')
            print ('Node %s has been added ' % v.get_id())
            
            targetGraph.add_vertex(v.get_id())
            print ('with our Neighbors ')
            for w in v.get_connections():  # for each Vertex get array of the neighbor data
                vid = v.get_id()
                wid = w.get_id()
                if wid not in unavailable_queue:
                    targetGraph.add_edge(vid,wid,v.get_weight(w))
                    print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w)))
                    
       
def loadInitialDefaultGraph(gGraph):
    try:
    #7    
    #1 2 100 10
    #1 4 200 30
    #1 6 80 10
    #2 3 50 10
    #2 5 180 20
    #3 4 50 5
    #3 6 150 20
    #4 5 100 10
            gGraph= None
            gGraph= Graph()
            gGraph.add_vertex('1')
            gGraph.add_vertex('2')
            gGraph.add_vertex('3')
            gGraph.add_vertex('4')
            gGraph.add_vertex('5')
            gGraph.add_vertex('6')
        
            gGraph.add_edge('1', '2', 10)  
            gGraph.add_edge('1', '4', 30)
            gGraph.add_edge('1', '6', 10)
            gGraph.add_edge('2', '3', 10)
            gGraph.add_edge('2', '5', 20)
            gGraph.add_edge('3', '4', 5)
            gGraph.add_edge('3', '6', 20)
            gGraph.add_edge('4', '5', 10)
            
            nodesNumber=6
            print ('Default Graph data:')
            print ('Nodes number %s' % nodesNumber)
            for v in gGraph: # Vertex list in Graph() object
                print ('Node %s. Is it available ?  %s' % (v.get_id(),v.get_available()) )
                print ('Neighbors ')
                for w in v.get_connections():  # for each Vertex get array of the neighbor data
                    vid = v.get_id()
                    wid = w.get_id()
                    print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w))
                        )
                        
    except Exception:
        print("Error loading and printing default graph data")
        
                    
def loadInitialGraph(gGraph,configFilePathNameParameter):
    #Reading config file
    dataInFile = []
    errorLoad =True
    try:
    # it is an example about data format to build configuration file   
    #6
    #1 2 100 10
    #1 4 200 30
    #1 6 80 10
    #2 3 50 10
    #2 5 180 20
    #3 4 50 5
    #3 6 150 20
    #4 5 100 10
            
            nodesNumber = 0
            if configFilePathNameParameter==None:
                configFilePathNameParameter=str(input("Please enter the name of the config file (ie.config.txt)"))
            print('Trying load Graph from File at ' , configFilePathNameParameter)    
            for line in open(configFilePathNameParameter):
                row=line.strip()
                # print('Line text %s' % row)
                dataInFile.append(row)
            fileinput.close()
            try:
                nodesNumber=int(dataInFile[0])
            except  Exception:
                nodesNumber = 0 
        
            #print (dataInFile)
            errorLoad=False
    except Exception:
        print("The configuration file has not been read")    
        print("Please check that the file is in the same folder as the program")
        
    if errorLoad== False:    
    
        #Loading Graph object from Data in File
        try:
            
            topography = []
            if nodesNumber == 0:
                for topoline in dataInFile[0:]:
                    topography.append(topoline.split(' '))
                    #print(topography)
            else:
                for topoline in dataInFile[1:]:
                    topography.append(topoline.split(' '))
                    #print(topography)
            #creating edges and nodes by default. See add_edge function detail
            for elementTopography in topography:
                gGraph.add_edge(elementTopography[0],elementTopography[1],int(elementTopography[3]))
                
            try:
                print ('Graph data:')
                print (' Nodes number %s ' % nodesNumber)
                for vertex in gGraph: # Vertex list in Graph() object
                    print ('Node %s.  Is it available ? %s' % (vertex.get_id(),vertex.get_available()) )
                    print ('Neighbors ')
                    for w in vertex.get_connections():  # for each Vertex get array of the neighbor data
                        vid = vertex.get_id()
                        wid = w.get_id()
                        print ('( %s , %s, %3d)'  % ( vid, wid, vertex.get_weight(w)))
                    
            except Exception:
                print("Error printing graph data")
            
        except Exception:
            print("exception loading configuration data from file - Creating table of coordinates")
        
            
    else:
         loadInitialDefaultGraph(gGraph)
    
       
def graphInstanceCreation(configurationPathFile):
#graph instance creation
# Declare empty g Object Graph 
    
    
    try:
        g = Graph()
        loadInitialGraph(g,configurationPathFile)
           
    except Exception as error_graph_loading:
         print("There was an error in Loading initial configuration to Graph.")
         print("However have been load a default data as example")
         print("Error Graph load config:", sys.exc_info()[0], ' Message ', sys.exc_info()[1])
    return g   


#Controller instance creation 
def controllerInstanceCreation(hostnameP,portNumberP):
                   
    try:
        controller = Controller()
        sockettimeout=10
            
        if hostnameP=='':
            print ("Please enter a valid host name and a well known port (from 0 - 1023)")
            hostnameP = str(input("Host Name: "))
            print("Host name captured is : ", hostnameP)
        if portNumberP=='':
            print("Recommended to choose port 8000 as well known port ")
            portNumberP = int(input("Number: "))
            print ("portNumber captured", portNumberP)
        controller.configuration( hostnameP, portNumberP)
        print("controller host registered is: ", controller.ControllerHost)
        print("controller port registered is: ", controller.ControllerPort)
    
    except Exception as error_controller_config:
        print("There was an error in the configuration of Controller hostname or portNumber.")
        print("Please check the type of the inputs")
        print("Error Controller config:", sys.exc_info()[0], ' Message ', sys.exc_info()[1])
    
    #Socket creation
    try:
        socket.setdefaulttimeout(sockettimeout)
        #int(input("Please enter the time of sockets' waiting responses: ")))    
        print ("Creating socket Controller")
        socketController = controller.socketCreation()
        
        print ("socket controller created")
        
    except Exception as error_socket_controller:
        print("Error with the arg associated with the creation of the socket controller.")
        print("Please check if the arguments are valid")
        print("Error socket creating:", sys.exc_info()[0], ' Message ', sys.exc_info()[1])  
    
    
    #socket binding
    try:
        print("socket binding in progress")
        args = controller.ControllerHost,controller.ControllerPort
        socketController.bind(args)
        # socketController.listen(backlog)  Just to Stream socket kind
        print("binded in host ", controller.ControllerHost, " in port ", controller.ControllerPort)
    except Exception as error_binding_controller:
        print("Error binding:", sys.exc_info()[0], ' Message ', sys.exc_info()[1])    

    return  socketController
def timeStampRightNow():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st
def register_response(gP,swIdP,socketP,addresP):
  
  nodeRequester = gP.get_vertex(swIdP)
  if nodeRequester!= None:
      try:
          controllerMsg = "REGISTER_RESPONSE"
          print('%s Sending the message %s: to socket  ' % (timeStampRightNow(),controllerMsg))
          
          socketP.sendto(controllerMsg.encode('utf-8'),addresP)
          print('%s The message was sent: %s ' % (timeStampRightNow(),controllerMsg))
          
                    
          initialNodeName=swIdP
          initialNode = gP.get_vertex(initialNodeName)
          
          if  initialNode!= None :        # To validate that initialNode Object to be different that None. Thats mean that is included in Graph
                  # To Update status node with set_available() and  timestamp properties
                  initialNode.set_available()
                  print(' %s Switch : %s has been registed LIVE' % (timeStampRightNow(),swIdP) )
                  initialNode.set_lastTime(time.time())
                  initialNode.set_socketAddress(addresP)
#                  
#                  # CHECK that All Nodes are registered
#                  AreThereAllNodes_REGISTERED = allNodesAreAvailables(gP,socketP)  # if it is true then set a internal variable called gP.startFirstTime='No' in Graph                  
#                  if (AreThereAllNodes_REGISTERED):
#                      print('Now We have all nodes registerde and we have update SHORT PATH for each ones')
#                      
                      
                  dinamicGraph = Graph()
                  neighbordict = {}
                  loadDinamicGraphWithAvailablesNodes(gP,dinamicGraph)
                  nodeInDynamicGraph=dinamicGraph.get_vertex(initialNodeName)
                  if nodeInDynamicGraph.available :  # To validate that initialNode Object is available into DynamicGraph
                       #  El nodo solicitante esta activo 
                        for w in nodeInDynamicGraph.get_connections():  # for each Vertex get array of the neighbor data
                            vid = nodeInDynamicGraph.get_id()
                            wid = w.get_id()   # this is a neighbord
                            #neighborMessage = neighborMessage + neighborMessage
                            print ('( %s , %s, %3d)'  % ( vid, wid, nodeInDynamicGraph.get_weight(w)))
                            neighbordict[wid]=  nodeInDynamicGraph.get_weight(w)
                        jsonString = json.dumps(neighbordict)
                        print('Neighbor List to Switch called %s is %s' % (initialNodeName,jsonString))
                        try:
                                neighborMessage =jsonString 
                                socketP.sendto(neighborMessage.encode('utf-8'),addresP)
                                print('Neighbor List to Switch called %s is %s . It were sent ' % (initialNodeName,jsonString))
                        except socket.timeout as error_neighborList_controller:
                                print("Error responding at sending neighbord List:", sys.exc_info()[0])
                        #continue 
                 
      except socket.timeout as error_time_out:
           print("Register response time out")
      #continue 
  else:
        try:
            controllerMsg = "REGISTER_RESPONSE"
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)
            
            print("Message sent: ", controllerMsg) 
            neighbordict={'Switch_Id_Isnt_Included_In_Graph'}
            controllerMsg = json.dumps(neighbordict)
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)

        except Exception as error_neighborList_controller:
            print("Error responding:", sys.exc_info()[0])
        #continue                 
def topology_response(gP,swIdP,socketP,addresP):
  
  nodeRequester = gP.get_vertex(swIdP)
  if nodeRequester!= None:
      try:
         
          #msg=None
          controllerMsg = "TOPOLOGY_UPDATE"
          #msg = '%s,%s'  % ( 'TOPOLOGY_UPDATE', swIdP)
          print('%s Sending the message %s: to socket  ' % (timeStampRightNow(),controllerMsg))
          
          socketP.sendto(controllerMsg.encode('utf-8'),addresP)
          print('%s The message was sent: %s ' % (timeStampRightNow(),controllerMsg))
          
                    
          initialNodeName=swIdP
          initialNode = gP.get_vertex(initialNodeName)
          
          if  initialNode!= None :        # To validate that initialNode Object to be different that None. Thats mean that is included in Graph
                  # To Update status node with set_available() and  timestamp properties
                  initialNode.set_available()
                  print(' %s Switch : %s has been registed LIVE' % (timeStampRightNow(),swIdP) )
                  initialNode.set_lastTime(time.time())
                  #print('IpYAdress ' % addresP)
                  initialNode.set_socketAddress(addresP)
#                  # CHECK that All Nodes are registered
#                  AreThereAllNodes_REGISTERED = allNodesAreAvailables(gP,socketP)  # if it is true then set a internal variable called gP.startFirstTime='No' in Graph                  
#                  if (AreThereAllNodes_REGISTERED):
#                      print('Now We have all nodes registerde and we have update SHORT PATH for each ones')
#                      
#                  AreThereAllNodes_REGISTERED= True
#                      #if gP.areAllNodesRegistered==False :
#                 
#                      for v in gP: # Vertex list in Graph() object
#                          #print(v.available)
#                          if v.available =='No':
#                              print ('Node %s is Unavailable  '  % v.get_id())
#                              AreThereAllNodes_REGISTERED= False

                  


                  dinamicGraph = Graph()
                  neighbordict = {}
                  loadDinamicGraphWithAvailablesNodes(gP,dinamicGraph)
                  nodeInDynamicGraph=dinamicGraph.get_vertex(initialNodeName)
                  if nodeInDynamicGraph.available :  # To validate that initialNode Object is available into DynamicGraph
                       #  El nodo solicitante esta activo 
                        for w in nodeInDynamicGraph.get_connections():  # for each Vertex get array of the neighbor data
                            vid = nodeInDynamicGraph.get_id()
                            wid = w.get_id()   # this is a neighbord
                            #neighborMessage = neighborMessage + neighborMessage
                            print ('( %s , %s, %3d)'  % ( vid, wid, nodeInDynamicGraph.get_weight(w)))
                            neighbordict[wid]=  nodeInDynamicGraph.get_weight(w)
                        jsonString = json.dumps(neighbordict)
                        print(' Neighbor List to Switch called %s is %s' % (initialNodeName,jsonString))
                        try:
                                neighborMessage = jsonString     
                                socketP.sendto(neighborMessage.encode('utf-8'),addresP)
                        except socket.timeout as error_neighborList_controller:
                                print("Error responding at sending neighbord List:", sys.exc_info()[0])
                        #continue 
                 
      except socket.timeout as error_time_out:
           print("Register response time out")
      #continue 
  else:
        try:
            controllerMsg = "TOPOLOGY_UPDATE"
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)
            
            print("Message sent: ", controllerMsg) 
            neighbordict={'Switch_Id_Isnt_Included_In_Graph'}
            controllerMsg = json.dumps(neighbordict)
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)

        except Exception as error_neighborList_controller:
            print("Error responding:", sys.exc_info()[0])
        #continue                 
            


                    
def route_update_send(gP,swIdP,socketP,tupleIpAdd):
    
  # gP It is a graph
  # swIdP  It is a Node Id
  # socketP It is a Socket Object
  # addresP It is a tuple of Node
  try: 
    print("%s In Updating  ROUTE_UPDATE function " % (timeStampRightNow()))
    
    switcherID = swIdP
    print("%s Updating  ROUTE_UPDATE from Controller to Switch : %s " % (timeStampRightNow(),switcherID))
    nodeRequester = gP.get_vertex(switcherID)

    if nodeRequester!= None:
        # to check all nodes registed
        # update time
        nodeRequester.set_lastTime(time.time())
        
        print(' %s Switch : %s has been registed LIVE from route_update_Push ' % (timeStampRightNow(),swIdP) )      
        addresP=tupleIpAdd
        try:
            if switcherID  in gP.vert_dict:
                
              initialNodeName=switcherID
              print('Initial Nodo  %s' % initialNodeName)  
              dinamicGraph = Graph()
              loadDinamicGraphWithAvailablesNodes(gP,dinamicGraph)
              dinamicGraph.printGraph()
              resultShortPath = {}
              resultShortPath = dinamicGraph.getShortPathFrom(initialNodeName)  
              jsonString = json.dumps(resultShortPath)
              print(' Route table to Switch called %s is %s' % (initialNodeName,jsonString))
              try:
                controllerMsg = "ROUTE_UPDATE_PUSH"
                print('%s Sending the message %s: to socket  ' % (timeStampRightNow(),controllerMsg))
                socketP.sendto(controllerMsg.encode('utf-8'),addresP)
                print('%s The message was sent: %s ' % (timeStampRightNow(),controllerMsg))
                SwitchAnser = socketP.socket.recvfrom(1024)  
                print("Data from Switch received")
                data = SwitchAnser[0].decode('utf-8')
                addr = SwitchAnser[1]
                print ("Received message: ", data,"from", addr)
                print('Message ' , data)
                print('Address' , addr)  
                order=''
                if data:
                    msgSplited  = data.split(',')
                    order       = msgSplited[0]                
                if order == 'ROUTE_UPDATE_PUSH':
                    socketP.sendto(jsonString.encode('utf-8'),addresP)  
                    print("Route table sent: ", jsonString)
              except Exception as error_topology_update_controller:
                  print("Error responding to TOPOLOGY_UPDATE:", sys.exc_info()[0],sys.exc_info()[1])
        
        except socket.timeout as error_time_out:
           print("Topology response time out")
           #continue
        #else:
        #    print(" %s It is a first time that Controller start up and is not allow send  ROUTE_UPDATE " % (timeStampRightNow()))
    else:
       try:  # response containe topology empty
            controllerMsg = "ROUTE_UPDATE"
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)
            print("Message sent: ", controllerMsg) 
            resultShortPath={}
            controllerMsg = json.dumps(resultShortPath)
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)
       except Exception as error_neighborList_controller:
                    print("Error responding when response containe topology empty :", sys.exc_info()[0],sys.exc_info()[1])
                    
  except Exception as error_route_update_send:
                    print("route_update_send:", error_route_update_send.value)

def route_update_response(gP,swIdP,socketP,tupleIpAdd):
    
  # gP It is a graph
  # swIdP  It is a Node Id
  # socketP It is a Socket Object
  # addresP It is a tuple of Node
  try: 
    print("%s In Updating  ROUTE_UPDATE response function " % (timeStampRightNow()))
    
    switcherID = swIdP
    print("%s ROUTE_UPDATE  response: %s " % (timeStampRightNow(),switcherID))
    nodeRequester = gP.get_vertex(switcherID)

    if nodeRequester!= None:
        # to check all nodes registed
        # update time
        nodeRequester.set_lastTime(time.time())
        
        print(' %s Switch : %s has been registed LIVE from route_update_Push ' % (timeStampRightNow(),swIdP) )      
        addresP=tupleIpAdd
        try:
            
            controllerMsg = None
            if switcherID  in gP.vert_dict:
                
              initialNodeName=switcherID
              print('Initial Nodo  %s' % initialNodeName)  
              dinamicGraph = Graph()
              loadDinamicGraphWithAvailablesNodes(gP,dinamicGraph)
              dinamicGraph.printGraph()
              resultShortPath = {}
              resultShortPath = dinamicGraph.getShortPathFrom(initialNodeName)  
              jsonString = json.dumps(resultShortPath)
              print(' Route table to Switch called %s is %s' % (initialNodeName,jsonString))
              
              try:
                  controllerMsg = "ROUTE_UPDATE"
                  print('%s Sending the message %s: to socket  ' % (timeStampRightNow(),controllerMsg))
                  socketP.sendto(controllerMsg.encode('utf-8'),addresP)
                  print('%s The message was sent: %s ' % (timeStampRightNow(),controllerMsg))
                  
                  socketP.sendto(jsonString.encode('utf-8'),addresP)
                  print('%s The ROUTE Table was sent: %s ' % (timeStampRightNow(),controllerMsg))
                  print("Route table sent: ", jsonString)
              except Exception as error_topology_update_controller:
                  print("Error responding to TOPOLOGY_UPDATE:", sys.exc_info()[0],sys.exc_info()[1])
        
        except socket.timeout as error_time_out:
           print("Topology response time out")
           #continue
        #else:
        #    print(" %s It is a first time that Controller start up and is not allow send  ROUTE_UPDATE " % (timeStampRightNow()))
    else:
       try:  # response containe topology empty
            controllerMsg = "ROUTE_UPDATE"
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)
            print("Message sent: ", controllerMsg) 
            resultShortPath={}
            controllerMsg = json.dumps(resultShortPath)
            socketP.sendto(controllerMsg.encode('utf-8'),addresP)
       except Exception as error_neighborList_controller:
                    print("Error responding when response containe topology empty :", sys.exc_info()[0],sys.exc_info()[1])
                    
  except Exception as error_route_update_send:
                    print("route_update_send:", error_route_update_send.value)
                    
def allNodesAreAvailables(gP,socketP):
    try:
    #if gP.areAllNodesRegistered==False :
        for v in gP: # Vertex list in Graph() object
            #print(v.available)
            if v.available =='No':
                 print ('Node %s is Unavailable  '  % v.get_id())
                 return False
        # end for
        #gP.areAllNodesRegistered=True
        for v in gP:
            if v.available =='Yes':
                print('Disponible')
                if(v.iPsocketAddress == None):
                    print('The Node called %s has IPaddres NONE' % v.get_id())
                else:
                    print('Sending Update Route for the Node called %s has IPaddres %s' % (v.get_id(),v.iPsocketAddress))
                    
                swId=v.get_id() 
                
                ipAddTuple=v.iPsocketAddress
                iP=ipAddTuple[0]
                AddPort=ipAddTuple[1]
                
                print('swId %s' % swId )
                print('iP %s' % iP )
                print('Addr %s' % AddPort )
                route_update_response(swId)
                #route_update_send(gP,swId,socketP,iP,AddPort)   

        # end if
        return True
    except Exception as error_allNodesAreAvailables:
                    print("Error in allNodesAreAvailables ", error_allNodesAreAvailables.value)
        
            
        
    

def validateLiveNodes(gP,timeP,MKTimeP,socketP):
    
    try:
        
        # This function is requested every 0.001 seconds Just when select timeout is completed    
        # Parameters
        # gP It is our Graph Object
        # timeP  It is a time into while cicle from running after select 
        # MKTimeP It is a time criterial to consider Node dead
        # socketP It is our socket Object
        for v in gP: # Vertex list in Graph() object
            #print(v.available)
            if v.available =='Yes':
                nodeLastTime= float(v.lastTime)
                # print('Node number : %s has nodeLastTime : %f' % (v.id,nodeLastTime))
                # print('Current time : %f ' % (timeP))
                timeExp= timeP - nodeLastTime
                #print('Expiration time %f of %f ' % (timeExp,MKTimeP))
                if timeExp > MKTimeP:
                    gP.areAllNodesRegistered=False
                    v.available='No'
                    print(' %s Switch : %s has been registed dead' % (timeStampRightNow(),v.id) )
                    print(' %s Updating ROUTE_UPDATE to all actives nodes from validateLiveNodes function' % timeStampRightNow())
                    for v in gP:
                        if v.available =='Yes':
                            print('Updating short path to all actives nodes')
                            route_update_send(gP,v.id,socketP,v.iPsocketAddress)
    
    
                    
    except Exception as error_validateLiveNodes:
                    print("Error in validateLiveNodes ", error_validateLiveNodes.value)
                
                
                     
#Receiving requests from switches    
#while True:
def runProgram(hostnameP,portnumberP,configPathP,KTimeP):
    #if menu_choice == 1:
#listening to the switchers
        socketController=controllerInstanceCreation(hostnameP,portnumberP)
        g=graphInstanceCreation(configPathP)
        # just for debug    time.sleep(10)
        input = [socketController,sys.stdin] 
        running = 1
        MKtime= int(g.num_vertices) * int(KTimeP)
        mktrime= float(MKtime)
        print()
        print ('MK time to consider KEEP ALIVE for ones Switch is : %f seconds' % mktrime)
        print()
        print ('Controller is listen in %s with port %s' % (hostnameP,portnumberP))
        print ('Press Enter key to End program, ')
        while running:
            # To validate that all vertex are availables , if yes then send TOPOLOGY UPDATED Just in Start up process
            
                        
            inputready,outputready,exceptready = select.select(input,[],[],0.001)  # select has timeout  = 0.001 seconds
            
            for s in outputready:
                if s == socketController:
                    print('% s Evento de salida del socket ' % timeStampRightNow())
        
            for s in inputready: 
        
                if s == socketController:   # (1) We have received a request and go to handle all others sockets section below (2)
                    # handle the server socket 
                    try:
                        print("Now is expecting to receive info from switches")                     
                        d = socketController.recvfrom(1024)
                        print("Data received")
                        data = d[0].decode('utf-8')
                        addr = d[1]
                        print ("Received message: ", data,"from", addr)
                        print('Message ' , data)
                        print('Address' , addr)
                        order=''
                        if data:
                            msgSplited  = data.split(',')
                            order       = msgSplited[0]
                            swId        = msgSplited[1]
                            address     = addr[1]
                            iP          = addr[0]
                            print('Order is %s' % order )
                            print('Switch Id is %s' % swId )
                            
                            if order == 'REGISTER_REQUEST':
                                   print ('Sendind REGISTER_RESPONSE to Switch %s at  %s  Ip and %s address' %(swId,iP,address)) 
                                   register_response(g,swId,s,addr)                  
                            elif order == 'TOPOLOGY_UPDATE':
                                   print ('Sendind TOPOLOGY_RESPONSE to Switch %s at  %s  Ip and %s address' %(swId,iP,address)) 
                                   topology_response(g,swId,s,addr)
                            elif order == 'ROUTE_UPDATE':
                                   print ('Sendind  ROUTE_RESPONSE to Switch %s at  %s  Ip and %s address' %(swId,iP,address)) 
                                   route_update_response(g,swId,s,addr)       
                        
                            else:
                                print('Order is not know')
                                   
                        else:
                            print('None data')
                    except Exception:
                        print("Error in select.select for Implementation:", sys.exc_info()[0], sys.exc_info()[1])
                    
                        
                            #s.close() 
                            #input.remove(s)
                        
                elif s == sys.stdin: 
                    # handle standard input 
                    ketEntered = sys.stdin.readline()
                    running = 0
               
                else:
                    print('handle all other sockets')
  
                       
            # End for
            # validate LIVE nodes
            #print('time' , time.time())
            
            validateLiveNodes(g,time.time(),mktrime,socketController)
                
            # else UPDATE Topology
                        
        # End while running
        print('Controller program has terminated')
        socketController.close()   
  
    
    
    
def main(argv):
   hostnameParameter = None
   hostportParameter = None 
   configPathFileParameter=None
   arguments=0
   KTime=None
   try:
      #opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
      opts, args = getopt.getopt(argv,"h:n:p:f:k:",["hostnameParameter=","hostportParameter=","configPathFileParameter=","KTime="])
      arguments=args
   except getopt.GetoptError:
       print ('Controller.py -n <controller hostname>  -p <controller port> -f <config path file> -k <refress time to KEEP LIVE')
       #print( 'Controller.py -i <inputfile> -o <outputfile>')
       sys.exit(2)
   for opt, arg in opts:
       if opt == '-h':   # Requested Help to use it
         print ('Controller.py -n <controller hostname>  -p <controller port> -f <config path file> -k <refress time to KEEP LIVE')
         sys.exit()
       
       elif opt in ("-n", "--hostnameParameter"):
         hostnameParameter = arg
         
       elif opt in ("-p", "--hostportParameter"):
         hostportParameter = arg
         
       elif opt in ("-f", "--configPathFileParameter"):
         configPathFileParameter = arg
         
       elif opt in ("-k", "--KTime"):
         KTime = arg 
         
         
   # print ('Argumentos', len(arguments))
   if len(arguments)== 0:
          if hostnameParameter==None:
              hostnameParameter = 'localhost'
          if hostportParameter==None:
              hostportParameter= 8000
          if configPathFileParameter==None:   
              configPathFileParameter='config.txt' 
          if KTime==None:
              KTime=float(5)
              
          print('Controller program has been started ')      
          print ('Host name is ', hostnameParameter)
          print ('Port number is ', hostportParameter)
          print ('Configuration file to define Graph is ' ,configPathFileParameter)
          print ('K time for refresh KEEP ALIVE is : %s seconds' % KTime)
          #print('Host Name by Default is %s Host port Number by Default is %d and Configuration file by default is %s ' % (hostnameParameter,hostportParameter,configPathFileParameter))
          runProgram(hostnameParameter,hostportParameter,configPathFileParameter,KTime)
          
   
   
if __name__ == "__main__":
   main(sys.argv[1:])  
    
    
    
    