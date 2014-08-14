import time

watch_dict = {}

def load_module(bot):
    pass

def add_notify(bot, username, watch_username):
    watch_dict.setdefault(watch_username, set())
    watch_dict[watch_username].add(username)
    bot.msg(username, 'Adding %s to your notification list' % watch_username)

def check_notify(bot, username):
    if username in watch_dict:
        for user in watch_dict[username]:
            bot.msg(user, '%s is here' % (username,))
        del(watch_dict[username])
