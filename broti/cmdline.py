import sys
import sqlite3
import json
import logging
import configparser

from broti.bot import Bot

def execute():
    if len(sys.argv) < 2:
        print("Usage: %s command [options]" % sys.argv[0])
        print("Valid commands are:")
        print("- bot: start the bot")
        sys.exit(1)
    
    if sys.argv[1] == 'bot':
        start_bot(sys.argv)

def start_bot(argv):
    if len(argv) < 3:
        print("Usage: %s bot config-file" % sys.argv[0])
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config.read(argv[2])

    for section in config.sections():
        host, _, port = section.partition(':')
        if not port:
            port = 6667

        bot = Bot(host, port, dict(config.items(section)))
        bot.start()


