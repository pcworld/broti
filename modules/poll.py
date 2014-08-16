import time

poll_active = False
poll = {}
voted = set()

def start_poll(bot, replyto, username, args):
    global poll
    global poll_active
    global voted

    print(args)
    if len(args) < 1:
        bot.msg(replyto, 'Please specify some options')
        return

    print(args)

    poll_active = True

    bot.factory.logger.debug('Starting poll for %s with options %s' \
        % (username, ' '.join(args)))

    poll = dict([(option, 0) for option in args])
    print(poll)
    bot.msg(replyto, 'Poll started. Choose one among %s with *vote. You have 2 minutes.' % ', '.join(args))

    bot.hook_timeout(120, end_poll, replyto)

def do_poll(bot, replyto, username, args):
    global poll
    global poll_active
    global voted

    if len(args) < 1:
        return

    print(args)
    print(poll)

    if username in voted:
        bot.msg(replyto, 'You already voted. I am democratic, so each ' \
                'user only has one vote.')
    elif args[0] not in poll:
        bot.msg(replyto, 'This option is not part of the poll')
    else:
        bot.factory.logger.debug('%s voted on %s' % (username, args[0]))

        voted.add(username)
        poll[args[0]] += 1

def end_poll(bot, replyto):
    global poll
    global poll_active
    global voted

    bot.msg(replyto, 'Poll has ended. Here are the results:')
    for option, count in poll.items():
        bot.msg(replyto, '%s: %d' % (option, count))

def load_module(bot):
    bot.hook_command('poll', start_poll)
    bot.hook_command('vote', do_poll)
