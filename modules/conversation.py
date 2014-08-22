import sqlite3
import random

chain_length = 2
stop_word = u'\x02'
max_words = 7

def split_message(msg, length):
    sentence = msg
    words = sentence.split()

    if len(words) > length:
        words.insert(0, stop_word)
        words.append(stop_word)

        for i in range(len(words) - length):
            yield words[i:i + length + 1]

def random_probability(l):
    print(l)
    max_value = sum(el[1] for el in l)
    l = [(el[0], el[1] / max_value) for el in l]
    print(l)
    
    cur = random.random()
    for element, prob in l:
        cur -= prob

        if cur < 0:
            return element

    return element

def log_conversation(bot, c, e):
    markov_chains = split_message(e.arguments[0], chain_length)

    cur = bot.db.cursor()
    for chain in markov_chains:
        beginning = ' '.join(chain[:-1])
        continuation = chain[-1]

        try:
            cur.execute('''INSERT INTO speech_chains (beginning, continuation)
                VALUES (?, ?)''', (beginning, continuation))
        except sqlite3.IntegrityError:
            cur.execute('''UPDATE speech_chains SET cnt = cnt + 1
                WHERE beginning = ? AND continuation = ?''',
                (beginning, continuation))
    bot.db.commit()

def talk_back(bot, c, e, matches):
    bot.logger.debug('My name was mentioned in sentence "%s"' % matches[0])
    
    cur = bot.db.cursor()
    cur.execute('''SELECT * FROM speech_chains WHERE beginning LIKE ?
        ORDER BY RANDOM() LIMIT 1''', ('%s%%' % stop_word,))
    result = cur.fetchone()

    if result is None:
        return

    words = []
    for i in range(max_words - 1):
        if result[0].split()[0] != stop_word:
            words.append(result[0].split()[0])

        next_beginning = ' '.join((result[0].split()[1], result[1]))
        cur.execute('SELECT * FROM speech_chains WHERE beginning = ?',
            (next_beginning,))
        results = cur.fetchall()

        if len(results) == 0:
            break
        
        results = [(r[0:2], r[2]) for r in results]
        result = random_probability(results)

    words += next_beginning.split()
    bot.reply(c, e, ' '.join(words))

def load_module(bot):
    cur = bot.db.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS speech_chains (
        beginning TEXT,
        continuation TEXT,
        cnt INTEGER DEFAULT 1,
        CONSTRAINT unq UNIQUE (beginning, continuation))''')
    bot.db.commit()

    bot.hook_regexp('.*(?:^|\W)broti(?:$|\W).*', talk_back)
    bot.hook_action('privmsg', log_conversation)

    return [hash(talk_back)]
