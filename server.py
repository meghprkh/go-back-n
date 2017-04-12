#!/usr/bin/env python2

import socket
import pickle
import sys
import time
from transmit import transmit
from utilities import getHash

if len(sys.argv) < 2:
    print "Usage: ./server.py serverPort [timeout = 3]"
    exit(1)

# takes the port number as command line arguments and create server socket
serverIP = "127.0.0.1"
serverPort = int(sys.argv[1])
timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 3

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
        rcvpkt = []
        packet, clientAddress = serverSocket.recvfrom(4096)
        rcvpkt = pickle.loads(packet)
        # check value of checksum received (c) against checksum calculated (h) -
        # NOT CORRUPT
        c = rcvpkt[-1]
        del rcvpkt[-1]
        if c == getHash(rcvpkt):
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
                sndpkt = []
                sndpkt.append(expectedseqnum)
                sndpkt.append(getHash(sndpkt))
                transmit(serverSocket, pickle.dumps(sndpkt),
                         clientAddress[0], clientAddress[1])
                print "New Ack", expectedseqnum

            else:
                # default? discard packet and resend ACK for most recently
                # received inorder pkt
                print "Received out of order", rcvpkt[0]
                sndpkt = []
                sndpkt.append(expectedseqnum)
                sndpkt.append(getHash(sndpkt))
                transmit(serverSocket, pickle.dumps(sndpkt),
                         clientAddress[0], clientAddress[1])
                print "Ack", expectedseqnum
        else:
            print "error detected"
    except:
        if endoffile:
            if time.time() - lastpktreceived > timeout:
                break


endtime = time.time()

f.close()
print 'FILE TRANFER SUCCESSFUL'
print "TIME TAKEN ", str(endtime - starttime)
