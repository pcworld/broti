# -*- coding: utf-8 -*-

import functools

def manage(bot, c, e, args):
    username, _, _ = e.source.partition('!')
    if username != bot.config['owner']:
        bot.reply(c, e, 'Only %s can manage me' % bot.config['owner'])
        return

    bot.hook_action_oneshot('privnotice',
            functools.partial(do_command, args))
    c.privmsg('NickServ', 'ACC brati')

def do_command(command, bot, c, e):
    if not e.arguments[0].startswith('brati ACC'):
        return

    print(e.arguments[0].split())
    username, _, level = e.arguments[0].split()
    if username != bot.config['owner'] or int(level) < 3:
        c.privmsg(bot.config['owner'], 'Admin has to be authenticated')
        return

    if len(command) < 2:
        c.privmsg(bot.config['owner'],
                  'At least two arguments are required')
        return
    
    if command[0] == 'module.add':
        self.bot.load_module(command[1])
    elif command[0] == 'module.del':
        self.bot.unload_module(command[1])
    elif command[0] == 'channel.join':
        c.join(command[1])
    elif command[0] == 'channel.part':
        c.part(command[1])

def load_module(bot):
    bot.hook_command('manage', manage)

    return [hash(manage)]

def commands():
    return [('manage', 'Manage broti if you\'re owner',
             'manage [action] [options]')]
