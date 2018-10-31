import logging
import os
import py_translator
import random
from .temple import temple


def translate(bot, c, e, args):
    cmd = e.arguments[0].split()[0][1:]
    if cmd == 'smarttemple' and len(args) < 1:
        args.append('de') # default to 'de'
    elif cmd in ['translate', 'smarttranslate'] and len(args) < 2:
        bot.reply(c, e, 'Usage: dest-language string')
        return

    if args[0] not in py_translator.LANGUAGES:
        bot.reply(c, e, 'Invalid destination language "' + args[0] + '". See https://github.com/ssut/py-googletrans/blob/48653332effe76d0a034a730abdba1e96cd56d8a/googletrans/constants.py#L7')
        return

    if cmd.startswith('smart'):
        languages = random.sample(py_translator.LANGUAGES.keys(), 5)
        logging.info('translation languages: %s', languages)
    else:
        languages = []
    languages.append(args[0])

    if cmd == 'smarttemple':
        translated = temple()
    else:
        translated = ' '.join(args[1:])

    while languages:
        translated = py_translator.Translator().translate(text=translated, dest=languages.pop(0)).text
    bot.reply(c, e, translated)


def load_module(bot):
    bot.hook_command('translate', translate)
    bot.hook_command('smarttemple', translate)
    bot.hook_command('smarttranslate', translate)

    return [hash(translate)]


def commands():
    return [
        ('translate', 'translate', 'translate dest-language string; dest-language from https://github.com/ssut/py-googletrans/blob/48653332effe76d0a034a730abdba1e96cd56d8a/googletrans/constants.py#L7'),
        ('smarttranslate', 'Extremely smart translation', 'smarttranslate dest-language string; dest-language from https://github.com/ssut/py-googletrans/blob/48653332effe76d0a034a730abdba1e96cd56d8a/googletrans/constants.py#L7'),
        ('smarttemple', 'Smart version of *temple', 'smarttemple [dest-language]; dest-language from https://github.com/ssut/py-googletrans/blob/48653332effe76d0a034a730abdba1e96cd56d8a/googletrans/constants.py#L7')
    ]
