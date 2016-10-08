def overview(bot, c, e, args):
    if len(args) >= 1:
        command = None
        for module in bot.loaded_modules.values():
            try:
                for comm in module['object'].commands():
                    if comm[0] == args[0]:
                        command = comm
            except AttributeError:
                pass

        if command == None:
            bot.reply(c, e, 'This command does not exist')
        else:
            bot.reply(c, e, '%s (*%s)' % (command[1], command[2]))
    else:
        commands = []
        for module in bot.loaded_modules.values():
            try:
                commands += map(lambda x: x[0], module['object'].commands())
            except AttributeError:
                pass

        bot.reply(c, e, 'Commands: %s' \
                % ' '.join(map(lambda x: '*%s' % x, commands)))

def bot_usage(bot, c, e, matches):
    overview(bot, c, e, [])

def load_module(bot):
    bot.hook_command('help', overview)
    bot.hook_regexp('broti\W?\s*help', bot_usage)

    return [hash(overview), hash(bot_usage)]

def commands():
    return [('help', 'Display possible commands', 'help [command]')]
