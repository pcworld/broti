import time

def add_joined(bot, c, e):
    username, _, _ = e.source.partition('!')

    cur = bot.db.cursor()
    cur.execute('''INSERT INTO stalking (username, date, action, channel)
        VALUES (?, ?, ?, ?)''', (username, time.time(), 'join', e.target))
    bot.db.commit()
    
def add_left(bot, c, e):
    username, _, _ = e.source.partition('!')

    cur = bot.db.cursor()
    cur.execute('''INSERT INTO stalking (username, date, action, channel)
        VALUES (?, ?, ?, ?)''', (username, time.time(), 'leave', e.target))
    bot.db.commit()

def load_module(bot):
    cur = bot.db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS stalking (
        username TEXT,
        date INTEGER,
        action TEXT,
        channel TEXT
        )''')
    bot.db.commit()

    bot.hook_action('userJoined', add_joined)
    bot.hook_action('userLeft', add_left)

    return [hash(add_joined), hash(add_left)]
