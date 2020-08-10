import datetime
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from biohack_questions.src import mongoclient

logger = logging.getLogger(__name__)


AVG_HEART_RATE = 'AVG_HEART_RATE'
OXYGENATION = 'OXYGENATION'
STEPS = 'STEPS'
HOURS_OF_SLEEP = 'HOURS_OF_SLEEP'
FATIGUE = 'FATIGUE'
CONCENTRATION = 'CONCENTRATION'
DONE = 'DONE'


def start(update, context):
    update.message.reply_text('Type your average heart rate')
    return AVG_HEART_RATE


def provide_avg_heart_rate(update, context):
    value = update.message.text
    context.user_data['heart_rate'] = value
    update.message.reply_text('Type your oxygenation')
    return OXYGENATION


def provide_oxygenation(update, context):
    value = update.message.text
    context.user_data['oxygenation'] = value
    update.message.reply_text('How many steps did you make')
    return STEPS


def provide_steps(update, context):
    value = update.message.text
    context.user_data['steps'] = value
    update.message.reply_text('Type how many hours of sleep you had')
    return HOURS_OF_SLEEP


def provide_hours_of_sleep(update, context):
    value = update.message.text
    context.user_data['hours_of_sleep'] = value

    reply_keyboard = [['yes', 'no']]
    update.message.reply_text(
        'Are you fatigue?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FATIGUE


def provide_fatigue(update, context):
    value = update.message.text
    context.user_data['fatigue'] = value

    reply_keyboard = [['high', 'mild', 'weak', 'none']]
    update.message.reply_text(
        'How is your concentration?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONCENTRATION


def provide_concentration(update, context):
    value = update.message.text
    context.user_data['concentration'] = value
    update.message.reply_text('This is what we have now %s. Type /check to re-fill the data or /done to finish' % context.user_data)
    return DONE


def done_start_info(update, context):
    log_record_dict = {
        'username': update.message.from_user.username,
        'heart_rate': context.user_data['heart_rate'],
        'oxygenation': context.user_data['oxygenation'],
        'steps': context.user_data['steps'],
        'hours_of_sleep': context.user_data['hours_of_sleep'],
        'fatigue': context.user_data['fatigue'],
        'concentration': context.user_data['concentration'],
        'date': datetime.datetime.now(),
    }
    mongoclient.add_log_record(log_record_dict)
    update.message.reply_text('Wrote it down, thanks')
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def generate_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('check', start)],
        states={
            AVG_HEART_RATE: [MessageHandler(Filters.text, provide_avg_heart_rate)],
            OXYGENATION: [MessageHandler(Filters.text, provide_oxygenation)],
            STEPS: [MessageHandler(Filters.text, provide_steps)],
            HOURS_OF_SLEEP: [MessageHandler(Filters.text, provide_hours_of_sleep)],

            FATIGUE: [MessageHandler(Filters.regex('^(yes|no)$'), provide_fatigue)],
            CONCENTRATION: [MessageHandler(Filters.regex('^(high|mild|weak|none)$'), provide_concentration)],

            DONE: [
                CommandHandler('check', start),
                CommandHandler('done', done_start_info),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
