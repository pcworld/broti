import time

requires = ['db']

def add_joined(bot, c, e):
    username, _, _ = e.source.partition('!')

    cur = bot.provides['db'].cursor()
    cur.execute('''INSERT INTO stalking (username, date, action, channel)
        VALUES (?, ?, ?, ?)''', (username, time.time(), 'join', e.target))
    bot.provides['db'].commit()
    
def add_left(bot, c, e):
    username, _, _ = e.source.partition('!')

    cur = bot.provides['db'].cursor()
    cur.execute('''INSERT INTO stalking (username, date, action, channel)
        VALUES (?, ?, ?, ?)''', (username, time.time(), 'leave', e.target))
    bot.provides['db'].commit()

def load_module(bot):
    cur = bot.provides['db'].cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS stalking (
        username TEXT,
        date INTEGER,
        action TEXT,
        channel TEXT
        )''')
    bot.provides['db'].commit()

    bot.hook_action('userJoined', add_joined)
    bot.hook_action('userLeft', add_left)

    return [hash(add_joined), hash(add_left)]
