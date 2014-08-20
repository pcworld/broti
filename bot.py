#!/usr/bin/env python

import irc.bot
import irc.strings
import importlib
import configparser, logging
import re, threading

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, config):
        self.logger = logging.getLogger(server)

        nickname = config['nickname']
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.config = config

        self.commands = {}
        self.actions = {}
        self.regexps = []

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        for channel in self.config['channels'].split(','):
            c.join(channel)

        import modules
        for module in self.config['modules'].split(','):
            self.logger.info('Loading module "%s"' % module)
        
            m = importlib.import_module('.%s' % module, 'modules')
            m.load_module(self)

        print(self.channels)
    
    def on_join(self, c, e):
        self.execute_action(c, e, 'userJoined')

    def on_privmsg(self, c, e):
        self.on_msg(c, e)

    def on_pubmsg(self, c, e):
        self.on_msg(c, e)

    def on_msg(self, c, e):
        args = e.arguments[0].split()
        if args[0].startswith('*'):
            self.execute_command(c, e, args[0][1:], args[1:])

        self.execute_regexps(c, e, ' '.join(e.arguments))
        self.execute_action(c, e, 'privmsg')

    def reply(self, c, e, msg):
        if e.type == 'pubmsg':
            c.privmsg(e.target, msg)
        else:
            user, _, host = e.source.partition('!')
            c.privmsg(user, msg)

    def user_online(self, user):
        for channel in self.channels.values():
            if channel.has_user(user):
                return True

        return False

    def hook_command(self, command, function):
        self.logger.debug('Hooking to command "%s"' % command)
        self.commands.setdefault(command, [])
        self.commands[command].append(function)

    def hook_action(self, action, function):
        self.logger.debug('Hooking to action "%s"' % action)
        self.actions.setdefault(action, [])
        self.actions[action].append(function)

    def hook_regexp(self, regexp, function):
        self.logger.debug('Hooking to regexp "%s"' % regexp)
        self.regexps.append((regexp, function))

    def hook_timeout(self, timeout, function, c, replyto):
        threading.Timer(timeout, function, [c, self, replyto]).start()

    def execute_action(self, c, e, action):
        if action in self.actions:
            for f in self.actions[action]:
                f(self, c, e)

    def execute_regexps(self, c, e, msg):
        for r, f in self.regexps:
            m = re.match(r, msg)
            if m:
                f(self, c, e, m.groups())

    def execute_command(self, c, e, cmd, args):
        if cmd in self.commands:
            for f in self.commands[cmd]:
                f(self, c, e, args)

def main():
    logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config.read('config.ini')

    for section in config.sections():
        host, _, port = section.partition(':')
        if not port:
            port = 6667

        bot = Bot(host, port, dict(config.items(section)))
        bot.start()

if __name__ == "__main__":
    main()
