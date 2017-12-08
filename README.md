# Python_Switch_Simulator
Python implementation of a switch device to get a short path algorithm based on Dijkstra solution

### Implementation of Dijkstra’s computational algorithm to make a simulation of the short routing on nodes including at the network. 


***

The implementation built a couple of classes. Ones to Switch node simulation and other to the controller that runs the Dijkstra’s computation algorithm and sends the routing table to all switches.
Some requirements shows below
1.  The controller Manages concurrence
1.  The controller checks the registered nodes and validates that they are alive, then it is sent to each node its calculation of short route for all the active destinations.
1.  The controller detects that it has reached the waiting time -result of multiplying the number of nodes for a programmable time- for each node and has not registered or requested an update of neighbors, then we unsubscribe and update them to the ALL nodes active their short route.
1. The Switch asks each K time an update of Neighbors to the controller.
1. The programs receive a parameter from the command line called -k that represents the refresh time for the communications.
