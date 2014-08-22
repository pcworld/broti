#!/usr/bin/env python

import irc.bot
import irc.strings
import importlib
import configparser, logging
import re, threading
from multiprocessing.connection import Listener
import sqlite3

class BotManipulationListener(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot

    def run(self):
        address = ('localhost', 6000)
        key = self.bot.config['key']
        listener = Listener(address, authkey=bytes(key, 'ascii'))

        while True: # listen to infinite connections, one at a time
            conn = listener.accept()
            while True: # let one connection pass multiple commands
                try:
                    msg = conn.recv()
                    if msg['server'] == self.bot.server:
                        if msg['action'] == 'module.add':
                            self.bot.load_module(msg['value'])
                        elif msg['action'] == 'module.del':
                            self.bot.unload_module(msg['value'])
                except EOFError: # remote connection closed
                    break
        
            conn.close()
        listener.close()


# TODO: Dynamic loading of modules using sqlite not possible,
# because sqlite objects can only be used in one thread
# TODO: Add depends to each module so that bot can load
# stuff dynamic and also give error messages if e.g. database
# is not available
class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, config):
        self.logger = logging.getLogger(server)

        nickname = config['nickname']
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.config = config
        self.server = server
        self.start_listener()
        self.db = sqlite3.connect(config['db'])
        
        self.loaded_modules = {}

        self.commands = {}
        self.actions = {}
        self.regexps = []

    def start_listener(self):
        self.logger.info('Starting listener for online bot manipulation')

        t = BotManipulationListener(self)
        t.start()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        for channel in self.config['channels'].split(','):
            c.join(channel)

        import modules
        for module in self.config['modules'].split(','):
            self.load_module(module)

    def load_module(self, module):
        if module in self.loaded_modules:
            self.logger.debug('Module "%s" is already loaded' % module)
            return
        else:
            self.logger.info('Loading module "%s"' % module)

            m = importlib.import_module('.%s' % module, 'modules')
            hashes = m.load_module(self)

            self.loaded_modules[module] = {
                    'object': m,
                    'hashes': hashes
            }

    def unload_module(self, module):
        try:
            for h in self.loaded_modules[module]['hashes']:
                self.unhook_command(h)
                self.unhook_action(h)
                self.unhook_regexp(h)
            del(self.loaded_modules[module])
        except KeyError:
            self.logger.debug('Module "%s" is not loaded' % module)

    def on_join(self, c, e):
        self.execute_action(c, e, 'userJoined')

    def on_part(self, c, e):
        self.execute_action(c, e, 'userLeft')

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

    def unhook_command(self, h):
        self.logger.debug('Unhooking command with function pointer ' \
                'hash "%s"' % h)
        for command in self.commands:
            try:
                idx = list(map(hash, self.commands[command])).index(h)
                del(self.commands[command][idx])
                print('found command')
            except ValueError:
                pass

    def hook_action(self, action, function):
        self.logger.debug('Hooking to action "%s"' % action)
        self.actions.setdefault(action, [])
        self.actions[action].append(function)

    def unhook_action(self, h):
        self.logger.debug('Unhooking action with function pointer ' \
                'hash "%s"' % h)
        for action in self.actions:
            try:
                idx = list(map(hash, self.actions[action])).index(h)
                del(self.actions[action][idx])
            except ValueError:
                pass

    def hook_regexp(self, regexp, function):
        self.logger.debug('Hooking to regexp "%s"' % regexp)
        self.regexps.append((regexp, function))

    def unhook_regexp(self, h):
        self.logger.debug('Unhooking regexp with function pointer ' \
                'hash "%s"' % h)
        for i, (regexp, function) in enumerate(self.regexps):
            if hash(function) == h:
                del(self.regexps[i])

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
                f(self, c, e, [m.group(0)] + list(m.groups()))

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
