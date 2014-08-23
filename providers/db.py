import sqlite3

def load(bot):
    try:
        return None
        return sqlite3.connect(bot.config['db'])
    except ValueError:
        return None
