#!/usr/bin/env python2

import socket
import pickle
import sys
import time
from transmit import transmit
from utilities import parseAndVerify, makeACK

if len(sys.argv) < 2:
    print "Usage: ./server.py serverPort [timeout = 0.01]"
    exit(1)

# takes the port number as command line arguments and create server socket
serverIP = "127.0.0.1"
serverPort = int(sys.argv[1])
timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.settimeout(timeout)
print "Ready to serve"

# initializes packet variables
expectedseqnum = 1
ACK = 1
ack = []

# RECEIVES DATA
f = open("output", "wb")
endoffile = False
lastpktreceived = time.time()
starttime = time.time()


while True:

    try:
        packet, clientAddress = serverSocket.recvfrom(4096)
        rcvpkt, isCorrupt = parseAndVerify(packet)
        if not isCorrupt:
            # check value of expected seq number against seq number received -
            # IN ORDER
            if(rcvpkt[0] == expectedseqnum):
                print "Received inorder", expectedseqnum
                if rcvpkt[1]:
                    f.write(rcvpkt[1])
                else:
                    endoffile = True
                expectedseqnum = expectedseqnum + 1
                # create ACK (seqnum,checksum)
                sndpkt = makeACK(expectedseqnum)
                transmit(serverSocket, pickle.dumps(sndpkt),
                         clientAddress[0], clientAddress[1])
                print "New Ack", expectedseqnum

            else:
                # default? discard packet and resend ACK for most recently
                # received inorder pkt
                print "Received out of order", rcvpkt[0]
                sndpkt = makeACK(expectedseqnum)
                transmit(serverSocket, pickle.dumps(sndpkt),
                         clientAddress[0], clientAddress[1])
                print "Ack", expectedseqnum
        else:
            print "error detected"
    except:
        if endoffile:
            # if we dont recieve any packet for 3 seconds then we terminate
            # as client would have terminated after sending the whole file
            if time.time() - lastpktreceived > 3:
                break


endtime = time.time()

f.close()
print 'FILE TRANFER SUCCESSFUL'
print "TIME TAKEN ", str(endtime - starttime)
