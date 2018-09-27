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

    topic, question, solution = random.choice(questions)
    bot.reply(c, e, '%s: %s (solution will be revealed in 2 minutes)'
              % (topic, question))
    current_solution = solution

    bot.hook_timeout(120, end_quiz, c, e)


def end_quiz(bot, c, e):
    global current_solution

    bot.reply(c, e, 'Quiz has ended. Correct solution is: %s'
              % current_solution)

    current_solution = None


def load_module(bot):
    global questions

    data = []
    files = [
        'data/squad/questions_dev.json',
        'data/squad/questions_train.json',
    ]
    for filepath in files:
        with open(filepath) as f:
            data += json.load(f)['data']

    for topic_elem in data:
        topic = topic_elem['title']
        for par in topic_elem['paragraphs']:
            for qas in par['qas']:
                if not qas['is_impossible'] and len(qas['answers']) > 0:
                    question = qas['question']
                    answer = qas['answers'][0]['text']

                    questions.append((topic, question, answer))

    bot.hook_command('quiz', start_quiz)

    return [hash(start_quiz)]


def commands():
    return [('quiz', 'Start a new round of a quiz', 'quiz')]
