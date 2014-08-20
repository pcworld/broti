def overview(bot, c, e, args):
    print(e.type)
    print(e.source)
    print(e.target)
    print(e.arguments)
    bot.reply(c, e, 'Commands: *notify, *poll (*vote), *rage')

def load_module(bot):
    bot.hook_command('help', overview)
