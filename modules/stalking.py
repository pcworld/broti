import time

def add_joined(bot, replyto, username):
    cur = bot.factory.db.cursor()
    cur.execute('''INSERT INTO stalking (username, date, action)
        VALUES (?, ?, ?)''', (username, time.time(), 'join'))
    bot.factory.db.commit()
    
def add_left(bot, replyto, username):
    cur = bot.factory.db.cursor()
    cur.execute('''INSERT INTO stalking (username, date, action)
        VALUES (?, ?, ?)''', (username, time.time(), 'leave'))
    bot.factory.db.commit()

def load_module(bot):
    cur = bot.factory.db.cursor()
    bot.factory.db.execute('''CREATE TABLE IF NOT EXISTS stalking (
        username TEXT,
        date INTEGER,
        action TEXT
        )''')
    bot.factory.db.commit()

    bot.hook_action('userJoined', add_joined)
    bot.hook_action('userLeft', add_left)
