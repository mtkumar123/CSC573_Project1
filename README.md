# CSC573_Project1

## How to run the files:

The server.py file is run first and then we run the client.py file.

Since the servername is not taken from the command line during run time and is
manually coded, before running the files, we need to change the servername to the
hostname of the machine on which these files are to be run in the client.py file.

Server is run using the command : python server.py

Client is run using the command: python client.py

In order to run the peer to peer functionality, we open another new terminal and run the
client.py script again by running the command python client.py.

However, if you run two client sessions on different terminals on the same PC, the
hostname of the peer for those two client sessions will be the same. Therefore although
the two terminal client sessions will have different upload port numbers, since their
hostname is the same, when they register at the server, the terminal session which had
the most recent communication with the server; that will be the port number registered
to the hostname.

The client would then be asked to input the request type. The client can request for
ADD/LOOKUP/LIST
- If the client chooses to ADD an RFC that it has to the server, it will be asked for the RFC number to be added and the RFC title.
- If the client chooses to LOOKUP, it will be asked to type the RFC number and consequently the RFC title.
- If client chooses to get LISTED the RFCs Server is currently having information of, it should type in LIST when prompted to mention the request type.
- If the client wants to download an RFC from another peer, it should type in GET when prompted to type the request it will further be asked to type the RFC number it desires     to download and then the RFC title it wantes to download is asked.

