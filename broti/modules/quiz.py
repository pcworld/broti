import json
import random


questions = []
current_solution = None


def start_quiz(bot, c, e, args):
    # TODO: I assume global state breaks if the bot is in more than one channel
    global current_solution
    global questions

    if current_solution:
        bot.reply(c, e, 'There already is a quiz running.')
        return
    elif e.target not in bot.channels:
        # TODO: Should also be usable somewhere else
        bot.reply(c, e, 'This command can only be used in channels.')
        return

    bot.logger.debug('Starting quiz')

    question = random.choice(questions)
    timeout = 10 + 20 * question['level']
    full_question = '%s (%d secs): a) %s, b) %s, c) %s, d) %s' \
        % (question['question'], timeout, question['options'][0],
           question['options'][1], question['options'][2],
           question['options'][3])
    bot.reply(c, e, full_question)
    current_solution = question['answer']

    bot.hook_timeout(timeout, end_quiz, c, e)


def end_quiz(bot, c, e):
    global current_solution

    bot.reply(c, e, 'Quiz has ended. Correct solution is: %s'
              % current_solution)

    current_solution = None


def load_module(bot):
    global questions

    data = []
    files = [
        'data/wwm/questions.json',
    ]
    for filepath in files:
        with open(filepath) as f:
            for line in f:
                data.append(json.loads(line))

    questions = data

    bot.hook_command('quiz', start_quiz)

    return [hash(start_quiz)]


def commands():
    return [('quiz', 'Start a new round of a quiz', 'quiz')]
