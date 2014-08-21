import time

poll_active = False
poll = {}
allowed_users = set()
voted = set()

def start_poll(bot, c, e, args):
    global poll
    global poll_active
    global voted
    global allowed_users 

    if len(args) < 2:
        bot.reply(c, e, 'Please specify some options')
        return
    elif poll_active:
        bot.reply(c, e, 'There already is a poll running.')
        return
    elif e.target not in bot.channels:
        bot.reply(c, e, 'This command can only be used in channels.')
        return

    poll_active = True
    allowed_users = set(bot.channels[e.target].users())
    print(allowed_users)

    bot.logger.debug('Starting poll for %s with options %s' \
        % (e.source, ' '.join(args)))

    poll = dict([(option, 0) for option in args])
    bot.reply(c, e,'Poll started. Choose one among %s with *vote. You have 2 minutes.' % ', '.join(args))

    bot.hook_timeout(120, end_poll, c, e.target)

def do_poll(bot, c, e, args):
    global poll
    global poll_active
    global voted
    global allowed_users 

    if len(args) < 1:
        return

    username, _, _ = e.source.partition('!')
    vote = args[0]
    if not poll_active:
        bot.reply(c, e, 'No poll active at the moment. You may start one ' \
                'with *poll')
    if username in voted:
        bot.reply(c, e, 'You already voted. I am democratic, so each ' \
                'user has only one vote.')
    elif username not in allowed_users:
        bot.reply(c, e, 'You have not been in the channel, when the ' \
                'voting began. You are not allowed to vote.')
    elif vote not in poll:
        bot.reply(c, e, 'This option is not part of the poll.')
    else:
        voted.add(username)
        poll[vote] += 1
        bot.reply(c, e, 'Your vote has been accepted.')

def end_poll(bot, c, replyto):
    global poll
    global poll_active

    bot.privmsg(replyto, 'Poll has ended. Here are the results:')
    for option, count in poll.items():
        bot.privmsg(replyto, '%s: %d' % (option, count))

    poll_active = False

def load_module(bot):
    bot.hook_command('poll', start_poll)
    bot.hook_command('vote', do_poll)

    return [hash(start_poll), hash(do_poll)]
