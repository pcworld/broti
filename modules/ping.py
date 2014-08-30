import functools, threading

timeout = 60
to_be_removed = set()

def ping(bot, c, e, args):
    if len(args) >= 1 and args[0] == 'stop':
        ping_stop(bot, c, e, args)
    else:
        ping_start(bot, c, e, args)

def ping_start(bot, c, e, args):
    username, _, _ = e.source.partition('!')
    bot.reply(c, e, 'Adding you to the ping list')
    bot.hook_timeout(timeout, pong, c, username)

def ping_stop(bot, c, e, args):
    username, _, _ = e.source.partition('!')
    bot.reply(c, e, 'Removing you from the ping list. You will probably ' \
            'receive one more pong')
    to_be_removed.add(username)

def pong(bot, c, username):
    if username not in to_be_removed:
        threading.Timer(timeout, pong, [bot, c, username]).start()
    c.privmsg(username, 'ping pong pung')

def load_module(bot):
    bot.hook_command('ping', ping)

    return [hash(ping)]

def commands():
    return [('ping',
             'Attach/detach yourself to/from one ping each minute',
             'ping [stop]')]
