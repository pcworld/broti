import time

watch_dict = {}

def add_notify(bot, c, e, args):
    if len(args) < 1:
        bot.reply(c, e, 'Please pass a username to follow')
        return

    username, _, _ = e.source.partition('!')
    bot.logger.debug('Got notification command from %s for %s' \
        % (username, args[0]))

    watch_username = args[0]
    watch_dict.setdefault(watch_username, set())
    watch_dict[watch_username].add(username)
    bot.reply(c, e, 'Adding %s to your notification list' % watch_username)

def check_notify(bot, c, e):
    username, _, _ = e.source.partition('!')

    if username in watch_dict:
        bot.logger.debug('Found %s who is in watch list' % username)

        for user in watch_dict[username]:
            if bot.user_online(user):
                c.privmsg(user, '%s is here' % (username,))
                del(watch_dict[username])

def load_module(bot):
    bot.hook_command('notify', add_notify)
    bot.hook_action('privmsg', check_notify)

    return [hash(add_notify), hash(check_notify)]
