# -*- coding: utf-8 -*-
import random

swear_words = ['Putain!', 'ça me fait chier', 'Salope!',
        'Je m’en fou', 'Nique ta mere!', 'Ta Gueule!', 'Casse-toi!',
        'C’est des conneries!']

def do_rage(bot, c, e, args):
    bot.reply(c, e, random.choice(swear_words))

def load_module(bot):
    bot.hook_command('rage', do_rage)
