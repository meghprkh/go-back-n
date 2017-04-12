import hashlib
import pickle

def getHash(packet):
    h = hashlib.md5()
    h.update(pickle.dumps(packet))
    return h.digest()

def parseAndVerify(packet):
    # parse packet
    rcvpkt = pickle.loads(packet)
    # check value of checksum received (c) against checksum calculated (h) -
    # NOT CORRUPT
    c = rcvpkt[-1]
    del rcvpkt[-1]
    isCorrupt = getHash(rcvpkt) != c
    return rcvpkt, isCorrupt
