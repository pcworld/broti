import time

watch_dict = {}

# TODO: Check if watch_username is a valid user in channel

def add_notify(bot, replyto, username, args):
    if len(args) < 1:
        return

    bot.factory.logger.debug('Got notification command from %s for %s' \
        % (username, args[0]))

    watch_username = args[0]
    watch_dict.setdefault(watch_username, set())
    watch_dict[watch_username].add(username)
    bot.msg(replyto, 'Adding %s to your notification list' % watch_username)

def check_notify(bot, _, username):
    if username in watch_dict:
        bot.factory.logger.debug('Found %s who is in watch list' % username)

        for user in watch_dict[username]:
            bot.msg(user, '%s is here' % (username,))
        del(watch_dict[username])

def load_module(bot):
    bot.hook_command('notify', add_notify)
    bot.hook_action('privmsg', check_notify)
