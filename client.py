#!/usr/bin/env python2

import socket
import sys
import time
from transmit import transmit
from utilities import parseAndVerify, makePkt

if len(sys.argv) < 3:
    print "Usage: ./client.py serverPort fileToUpload [windowSize = 7] [timeout = 0.01]"
    exit(1)

timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01

# takes the port number as command line arguments
serverName = "127.0.0.1"
serverPort = int(sys.argv[1])

# takes the file name as command line arguments
filename = ''.join(sys.argv[2])

# create client socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(timeout)

# initializes window variables (upper and lower window bounds, position of
# next seq number)
base = 1
nextSeqnum = 1
windowSize = int(sys.argv[3]) if len(sys.argv) > 3 else 7
window = []

# SENDS DATA
fileOpen = open(filename, 'rb')
data = fileOpen.read(500)
done = False
lastackreceived = time.time()

while not done or window:
    # check if the window is full	or EOF has reached
    if (nextSeqnum < base + windowSize) and not done:
        # create packet(seqnum,data,checksum)
        sndpkt = makePkt(nextSeqnum, data)
        # send packet
        transmit(clientSocket, sndpkt, serverName, serverPort)
        print "Data sent #", nextSeqnum
        # increment variable nextSeqnum
        nextSeqnum = nextSeqnum + 1
        # check if EOF has reached
        if not data:
            done = True
        # append packet to window
        window.append(sndpkt)
        # read more data
        data = fileOpen.read(500)

    # RECEIPT OF AN ACK
    try:
        packet, serverAddress = clientSocket.recvfrom(4096)
        rcvpkt, isCorrupt = parseAndVerify(packet)
        if not isCorrupt:
            # packet received not corrupt
            print "Received ack for #", rcvpkt[0]
            # slide window and reset timer
            while rcvpkt[0] > base and window:
                lastackreceived = time.time()
                del window[0]
                base = base + 1
        else:
            # packet received corrupt
            print "Error: corrupt packet received"
    # TIMEOUT
    except:
        if time.time() - lastackreceived > timeout:
            # Resend all packets in window
            for i in window:
                transmit(clientSocket, i, serverName, serverPort)

fileOpen.close()

print "Connection closed"
clientSocket.close()
