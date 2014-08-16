#!/bin/env python2

from twisted.words.protocols import irc
from twisted.internet import protocol
import sys
from twisted.internet import reactor
import sqlite3
import ConfigParser
import importlib
import re
import logging
import threading


class BrotiBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.config['nickname']
    nickname = property(_get_nickname)

    def __init__(self):
        self.commands = {}
        self.actions = {}
        self.regexps = []

    def signedOn(self):
        for channel in self.factory.config['channels'].split(','):
            self.join(channel)
        self.factory.logger.info("Signed on as %s." % (self.nickname,))

        for module in self.factory.config['modules'].split(','):
            self.factory.logger.info('Loading module "%s"' % module)

            m = importlib.import_module('.%s' % module, 'modules')
            m.load_module(self)
        
    def joined(self, channel):
        self.factory.logger.info("Joined %s." % (channel,))
    
    def userJoined(self, user, channel):
        self.execute_action('userJoined', None, user)
    
    def userLeft(self, user, channel):
        self.execute_action('userLeft', None, user)

    def privmsg(self, user, channel, msg):
        user, _, host = user.partition('!')

        if channel == self.nickname:
            replyto = user
        else:
            replyto = channel
        
        if msg.startswith('*'):
            self.execute_command(msg, replyto, user)

        self.execute_regexps(msg, replyto, user)
        self.execute_action('privmsg', replyto, user)

    def hook_command(self, command, function):
        self.factory.logger.debug('Hooking to command "%s"' % command)
        self.commands.setdefault(command, [])
        self.commands[command].append(function)

    def hook_action(self, action, function):
        self.factory.logger.debug('Hooking to action "%s"' % action)
        self.actions.setdefault(action, [])
        self.actions[action].append(function)

    def hook_regexp(self, regexp, function):
        self.factory.logger.debug('Hooking to regexp "%s"' % regexp)
        self.regexps.append((regexp, function))

    def hook_timeout(self, timeout, function, replyto):
        threading.Timer(timeout, function, [self, replyto]).start()

    def execute_action(self, action, replyto, user):
        if action in self.actions:
            for f in self.actions[action]:
                f(self, replyto, user)

    def execute_regexps(self, msg, replyto, user):
        for r, f in self.regexps:
            m = re.match(r, msg)
            if m:
                f(self, msg, replyto, user, m.groups())

    def execute_command(self, msg, replyto, user):
        parts = msg[1:].split()
        if parts[0] in self.commands:
            for f in self.commands[parts[0]]:
                f(self, replyto, user, parts[1:])



class BrotiBotFactory(protocol.ClientFactory):
    protocol = BrotiBot

    def __init__(self, config):
        self.db = sqlite3.connect('db.sqlite')
        self.config = config
        self.logger = logging.getLogger(__name__)

    def clientConnectionLost(self, connector, reason):
        self.logger.warning("Lost connection (%s), reconnecting." % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        self.logger.error("Could not connect: %s" % (reason,))
        

def validate_section(config):
    errors = []
    if not 'nickname' in config:
        errors.append('"nickname" missing')
    if not 'channels' in config:
        errors.append('"channels" missing')
    if not 'modules' in config:
        errors.append('"modules" missing')

    return errors

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    for server in config.sections():
        c = dict(config.items(server))
        errors = validate_section(c)
        if len(errors):
            print('Section "%s" is invalid' % server)
            print('\n'.join(errors))
        else:
            reactor.connectTCP(server, 6667, BrotiBotFactory(c))
            reactor.run()
