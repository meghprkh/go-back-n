#!/usr/bin/env python2

from random import randint
import pickle

dummy = ' '
reorder = 0
counter = 1
error = 1
p = 5


def transmit(csocket, message, serverName, serverPort):
    global counter, error, reorder, dummy, p
    message = pickle.dumps(message)
    if (randint(1, p) % p) != 0:
        csocket.sendto(message, (serverName, serverPort))
        print 'Sends properly packet No ' + str(counter)

    else:
        # Make some error with probability p
        if error == 1:
            print 'Dropped a packet No ' + str(counter)
            error = 2

        elif error == 2:
            print 'Duplicated a packet No ' + str(counter)
            csocket.sendto(message, (serverName, serverPort))

            csocket.sendto(message, (serverName, serverPort))
            error = 3

        elif error == 3:
            if reorder == 1:
                print 're-ordering a packet No ' + str(counter)
                csocket.sendto(message, (serverName, serverPort))
                csocket.sendto(dummy, (serverName, serverPort))
                reorder = 0
                counter = counter + 1
                error = 4
            else:
                dummy = message
                reorder = 1
                counter = counter - 1

        elif error == 4:
            print 'creating packet errors packet No ' + str(counter)
            mylist = list(message)
            # get last char of the string
            x = ord(mylist[-1])
            x = x ^ 1

            mylist[-1] = chr(x)
            dummy = ''.join(mylist)

            csocket.sendto(dummy, (serverName, serverPort))
            error = 1

    counter = counter + 1
