import hashlib
import pickle

def getHash(packet):
    h = hashlib.md5()
    h.update(pickle.dumps(packet))
    return h.digest()
