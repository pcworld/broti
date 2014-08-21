#!/bin/env python

from multiprocessing.connection import Client
import sys
import configparser

if len(sys.argv) < 2:
    print('Please pass the server name of the bot to change as argument')
    sys.exit(1)

server = sys.argv[1]

config = configparser.ConfigParser()
config.read('config.ini')

address = ('localhost', 6000)
key = config.get(server, 'key')
conn = Client(address, authkey=bytes(key, 'ascii'))

action = input('Action:')
value = input('Value:')
conn.send({'server': server,
    'action': action,
    'value': value})
conn.close()
