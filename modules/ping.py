import functools, threading

timeout = 60
to_be_removed = set()

def ping(bot, c, e, args):
    username, _, _ = e.source.partition('!')
    bot.reply(c, e, 'Adding you to the ping list')
    bot.hook_timeout(timeout, functools.partial(pong, username), c, username)

def ping_stop(bot, c, e, args):
    username, _, _ = e.source.partition('!')
    bot.reply(c, e, 'Removing you from the ping list')
    to_be_removed.add(username)

def pong(bot, c, username):
    if username not in to_be_removed:
        threading.Timer(timeout, pong, [bot, c, username]).start()
    bot.privmsg(username, 'ping pong pung')

def load_module(bot):
    bot.hook_command('ping', ping)
    bot.hook_command('ping_stop', ping_stop)

    return [hash(ping), hash(ping_stop)]

def commands():
    return [('ping', 'Attach yourself for being pinged each minute',
            'ping'),
            ('ping_stop', 'Stop being pinged', 'ping_stop')]