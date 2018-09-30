import json
import random
import glob
import os


questions = {}
user_answers = {}
current_solution = None


requires = ['db']


def start_quiz(bot, c, e, args):
    # TODO: I assume global state breaks if the bot is in more than one channel
    global current_solution
    global questions
    global user_answers

    if current_solution:
        bot.reply(c, e, 'There already is a quiz running.')
        return
    elif e.target not in bot.channels:
        # TODO: Should also be usable somewhere else
        bot.reply(c, e, 'This command can only be used in channels.')
        return
    elif len(args) < 1:
        datasets = ', '.join(questions.keys())
        bot.reply(c, e, 'Please specify a dataset name: %s' % datasets)
        return

    bot.logger.debug('Starting quiz')

    dataset = args[0]

    if dataset not in questions:
        bot.reply(c, e, 'Dataset "%s" does not exist' % dataset)
        return

    question = random.choice(questions[dataset])
    timeout = 20 + 25 * question['level']
    full_question = '%s (%d secs): a) %s, b) %s, c) %s, d) %s' \
        % (question['question'], timeout, question['options'][0],
           question['options'][1], question['options'][2],
           question['options'][3])
    bot.reply(c, e, full_question)
    current_solution = question['answers']
    user_answers = {}

    bot.hook_timeout(timeout, end_quiz, c, e)


def save_answers(bot, c, e, matches):
    if not current_solution:
        return

    username, _, _ = e.source.partition('!')
    print(matches)
    print(e.arguments)
    user_answers[username] = e.arguments[0]


def end_quiz(bot, c, e):
    global current_solution
    global user_answers

    correct_users = [user for user, answer in user_answers.items()
                     if answer in current_solution]

    bot.reply(c, e, 'Quiz has ended. Correct solution is: %s'
              % ', '.join(current_solution))

    conn = bot.provides['db'].get_conn()
    cursor = conn.cursor()
    for username in correct_users:
        cursor.execute('''INSERT OR IGNORE INTO quiz_score (username, score)
                          VALUES (?, ?)''', (username, 0))
        cursor.execute('''UPDATE quiz_score SET score = score + 1
                          WHERE username = ?''', (username,))
        conn.commit()

    current_solution = None


def quiz_score(bot, c, e, args):
    conn = bot.provides['db'].get_conn()
    cursor = conn.cursor()

    cursor.execute('''SELECT username, score FROM quiz_score
                      ORDER BY score DESC
                      LIMIT 10''')
    score_outs = []
    for row in cursor:
        score_outs.append('%s: %d' % row)

    bot.reply(c, e, ', '.join(score_outs))


def load_module(bot):
    global questions

    conn = bot.provides['db'].get_conn()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS quiz_score (
        username TEXT NOT NULL UNIQUE,
        score INTEGER NOT NULL
        )''')
    conn.commit()

    for filepath in glob.glob('data/quiz/*.json'):
        set_name = os.path.splitext(os.path.basename(filepath))[0]
        data = []
        with open(filepath) as f:
            for line in f:
                data.append(json.loads(line))

        questions[set_name] = data

    bot.hook_command('quiz', start_quiz)
    bot.hook_command('quiz-score', quiz_score)
    bot.hook_regexp('.*', save_answers)

    return [hash(start_quiz), hash(quiz_score), hash(save_answers)]


def commands():
    return [('quiz', 'Start a new round of a quiz', 'quiz set-name'),
            ('quiz-score', 'Show the current score', 'quiz-score')]
