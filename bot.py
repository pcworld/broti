#!/bin/env python2

from twisted.words.protocols import irc
from twisted.internet import protocol
import sys
from twisted.internet import reactor
import sqlite3

from modules import stalking, notify, info

class BrotiBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def __init__(self):
        self.commands = {}
        self.actions = {}

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)
        
        stalking.load_module(self)
        notify.load_module(self)
        info.load_module(self)

    def joined(self, channel):
        print "Joined %s." % (channel,)
    
    def userJoined(self, user, channel):
        stalking.add_joined(self, user)
    
    def userLeft(self, user, channel):
        stalking.add_left(self, user)

    def privmsg(self, user, channel, msg):
        user, _, host = user.partition('!')

        if channel.strip('_') == self.factory.nickname:
            replyto = user
        else:
            replyto = channel
        
        if msg.startswith('*'):
            parts = msg[1:].split()
            for command in self.commands:
                if parts[0] == command:
                    for f in self.commands[command]:
                        f(self, replyto, user, parts[1:])

        for f in self.actions['privmsg']:
            f(self, replyto, user)

    def hook_command(self, command, function):
        self.commands.setdefault(command, [])
        self.commands[command].append(function)

    def hook_action(self, action, function):
        self.actions.setdefault(action, [])
        self.actions[action].append(function)


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
    chan = "kitinfo-test"
    reactor.connectTCP('irc.freenode.net', 6667, BrotiBotFactory('#' + chan))
    reactor.run()
