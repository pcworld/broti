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

def load_module(bot):
    bot.hook_command('help', overview)

    return [hash(overview)]

def commands():
    return [('help', 'Display possible commands', 'help [command]')]
