#!/bin/env python2

from twisted.words.protocols import irc
from twisted.internet import protocol
import sys
from twisted.internet import reactor
import sqlite3

from modules import stalking

class BrotiBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)
        
        stalking.load_module(self)

    def joined(self, channel):
        print "Joined %s." % (channel,)
    
    def userJoined(self, user, channel):
        stalking.add_joined(self, user)
    
    def userLeft(self, user, channel):
        stalking.add_left(self, user)

    def privmsg(self, user, channel, msg):
        print msg

class BrotiBotFactory(protocol.ClientFactory):
    protocol = BrotiBot

    def __init__(self, channel, nickname='broti'):
        self.channel = channel
        self.nickname = nickname
        self.db = sqlite3.connect('db.sqlite')

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)
        

if __name__ == "__main__":
    chan = "kitinfo"
    reactor.connectTCP('irc.freenode.net', 6667, BrotiBotFactory('#' + chan))
    reactor.run()
