import time

def load_module(bot):
    cur = bot.factory.db.cursor()
    bot.factory.db.execute('''CREATE TABLE IF NOT EXISTS stalking (
        username TEXT,
        date INTEGER,
        action TEXT
        )''')
    bot.factory.db.commit()

def add_joined(bot, username):
    cur = bot.factory.db.cursor()
    cur.execute('''INSERT INTO stalking (username, date, action)
        VALUES (?, ?, ?)''', (username, time.time(), 'join'))
    bot.factory.db.commit()
    
def add_left(bot, username):
    cur = bot.factory.db.cursor()
    cur.execute('''INSERT INTO stalking (username, date, action)
        VALUES (?, ?, ?)''', (username, time.time(), 'leave'))
    bot.factory.db.commit()
