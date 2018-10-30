import json
import random
import glob
import os
import string
from collections import OrderedDict


questions = {}
user_answers = OrderedDict()
current_question = None
current_solution = None
formatted_solution = None
possible_solutions = None


requires = ['db']


def start_quiz(bot, c, e, args):
    # TODO: I assume global state breaks if the bot is in more than one channel
    global current_question
    global current_solution
    global formatted_solution
    global possible_solutions
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

    current_question = question = random.choice(questions[dataset])
    timeout = question['time'] if 'time' in question else 20 + 25 * question['level']
    full_question = '%s (%d secs)' % (question['question'], timeout)
    if 'options' in question:
           full_question += ': ' + ', '.join([string.ascii_lowercase[i] + ') ' + option for i, option in enumerate(question['options'])])

    bot.reply(c, e, full_question)
    current_solution = question['answers'].copy()
    if 'options' in question:
        current_solution += [string.ascii_lowercase[i] for i, answer in enumerate(question['options']) if answer in question['answers']]
        formatted_solution = ', '.join([string.ascii_lowercase[i] + ') ' + answer for i, answer in enumerate(question['options']) if answer in question['answers']])
        possible_solutions = question['options'] + list(string.ascii_lowercase[:len(question['options'])])
    else:
        formatted_solution = ', '.join(question['answers'])
        possible_solutions = question['answers']

    user_answers = OrderedDict()
    bot.hook_timeout(timeout, end_quiz, c, e)


def save_answers(bot, c, e, matches):
    global current_solution
    global possible_solutions

    if not current_solution:
        return

    username, _, _ = e.source.partition('!')
    answer = e.arguments[0]

    if answer.lower() in map(str.lower, possible_solutions):
        if username in user_answers:
            user_answers.move_to_end(username)
        user_answers[username] = e.arguments[0]


def end_quiz(bot, c, e):
    global formatted_solution
    global current_question
    global current_solution
    global user_answers

    correct_users = [user for user, answer in user_answers.items()
                     if answer.lower() in map(str.lower, current_solution)]

    # Scores: If there were correct answers, in total we reward as many points as users participated in the quiz.
    # The user with the first correct answer is rewarded 2 * base_score points, all other correct users are rewarded base_score points each.
    # This scheme incentivizes that many users participate, and correctly answering difficult questions (user answers are spread out evenly among the options) results in a higher reward. Furthermore the first correct user gets a bonus over imitators.
    # Note that this does not work well when a question does not have any 'options', as the number of participants cannot be measured.
    base_score = len(user_answers) / (1 + len(correct_users))

    res = 'Quiz has ended. Correct solution is: %s (%d %swere right).' \
        % (formatted_solution, len(correct_users),
           'out of ' + str(len(user_answers)) + ' ' if 'options' in current_question else '')
    if correct_users:
        res += ' %.1f p. for %s' % (2 * base_score, prevent_highlight(correct_users[0]))
        if len(correct_users) > 1:
            res += ' (first), %.1f p. for rest' % base_score
        res += '.'
    bot.reply(c, e, res)

    if 'explanation' in current_question and current_question['explanation']:
        bot.reply(c, e, current_question['explanation'])

    conn = bot.provides['db'].get_conn()
    cursor = conn.cursor()
    for i, username in enumerate(correct_users):
        cursor.execute('''INSERT OR IGNORE INTO quiz_score (username, score)
                          VALUES (?, ?)''', (username, 0))
        score = 2 * base_score if i == 0 else base_score # user with first correct answer gets bonus
        cursor.execute('''UPDATE quiz_score SET score = score + ?
                          WHERE username = ?''', (score, username))
        conn.commit()

    current_solution = None


def quiz_score(bot, c, e, args):
    conn = bot.provides['db'].get_conn()
    cursor = conn.cursor()

    if len(args) > 0:
        username = args[0]

        cursor.execute('''SELECT score FROM quiz_score
                          WHERE username = ?''', (username,))
        row = cursor.fetchone()
        score = row[0] if row else 0
        bot.reply(c, e, '%s: %d' % (prevent_highlight(username), score))
    else:
        cursor.execute('''SELECT username, score FROM quiz_score
                          ORDER BY score DESC
                          LIMIT 10''')
        score_outs = []
        for username, score in cursor:
            score_outs.append('%s: %d' % (prevent_highlight(username), score))

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
                if not line.startswith('#') and line.strip(): # not comment or empty line
                    question = json.loads(line)
                    # remove empty options (they might exist due to conversion from other formats)
                    if 'options' in question:
                        question['options'] = [o for o in question['options'] if o]
                    data.append(question)

        questions[set_name] = data

    bot.hook_command('quiz', start_quiz)
    bot.hook_command('quiz-score', quiz_score)
    bot.hook_regexp('.*', save_answers)

    return [hash(start_quiz), hash(quiz_score), hash(save_answers)]


def commands():
    return [('quiz', 'Start a new round of a quiz', 'quiz set-name'),
            ('quiz-score', 'Show the current score. Each quiz rewards as many points as the number of players who participate. The first correct user gets twice the points.', 'quiz-score [user]')]


def prevent_highlight(username):
    # use ZERO WIDTH NO-BREAK SPACE so that users' clients don't notify them
    return username[0] + '\ufeff' + username[1:]
