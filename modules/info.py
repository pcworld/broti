def overview(bot, replyto, user, args):
    bot.msg(replyto, 'Commands: *notify, *rage')

def load_module(bot):
    bot.hook_command('help', overview)
