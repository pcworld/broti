import os


# Needs package "wamerican" on Ubuntu, "words" on Arch
def temple():
    return os.popen("shuf -n32 /usr/share/dict/words --random-source=/dev/urandom | tr '\\n' ' '").read()


def temple_cmd(bot, c, e, args):
    bot.reply(c, e, 'God says: ' + temple())


def load_module(bot):
    bot.hook_command('temple', temple_cmd)

    return [hash(temple_cmd)]


def commands():
    return [('temple', 'Space alien trading post. https://archive.org/details/TempleOS-TheMissingVideos/20170310+(KUKqmsV7ccA)+Terry+A+Davis+Live+Stream.mp4 2:43:25', 'temple')]
