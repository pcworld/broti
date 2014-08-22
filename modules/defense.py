def defend_brati(bot, c, e, matches):
    bot.logger.debug('brati was hit, hitting back')

    username, _, _ = e.source.partition('!')
    bot.reply(c, e, '-slap %s' % username)

def load_module(bot):
    bot.hook_regexp('\-slap\sbrati', defend_brati)

    return [hash(defend_brati)]
