import datetime
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from biohack_questions.src import mongoclient

logger = logging.getLogger(__name__)


HEART_RATE_ASKED = 'HEART_RATE_ASKED'
OXYGENATION_ASKED = 'OXYGENATION_ASKED'
BED_TIME = 'BED_TIME'
STEPS_ASKED = 'STEPS_ASKED'
SLEEP_DURATION_ASKED = 'SLEEP_DURATION_ASKED'
FATIGUE_ASKED = 'FATIGUE_ASKED'
CONCENTRATION_ASKED = 'CONCENTRATION_ASKED'
DONE = 'DONE'


def start_and_ask_heart_rate(update, context):
    update.message.reply_text('Укажите показания сердечного ритма')
    return HEART_RATE_ASKED


def get_heart_rate_and_ask_oxygenation(update, context):
    value = update.message.text
    context.user_data['heart_rate'] = value
    update.message.reply_text('Укажите количество пройденных шагов за день')
    return OXYGENATION_ASKED


def get_oxygenation_and_ask_steps(update, context):
    value = update.message.text
    context.user_data['oxygenation'] = value
    update.message.reply_text('Напишите сколько часов вы сегодня спали?')
    return STEPS_ASKED


def get_steps_and_ask_sleep_duration(update, context):
    value = update.message.text
    context.user_data['steps'] = value
    update.message.reply_text('Type how many hours of sleep you had')
    return SLEEP_DURATION_ASKED


def get_sleep_duration_and_ask_fatigue(update, context):
    value = update.message.text
    context.user_data['hours_of_sleep'] = value

    reply_keyboard = [['yes', 'no']]
    update.message.reply_text(
        'Are you fatigue?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FATIGUE_ASKED


def get_fatigue_and_ask_concentration(update, context):
    value = update.message.text
    context.user_data['fatigue'] = value

    reply_keyboard = [['high', 'mild', 'weak', 'none']]
    update.message.reply_text(
        'How is your concentration?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONCENTRATION_ASKED


def get_concentration_and_summarize(update, context):
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
        entry_points=[CommandHandler('check', start_and_ask_heart_rate)],
        states={
            HEART_RATE_ASKED: [MessageHandler(Filters.text, get_heart_rate_and_ask_oxygenation)],
            OXYGENATION_ASKED: [MessageHandler(Filters.text, get_oxygenation_and_ask_steps)],
            STEPS_ASKED: [MessageHandler(Filters.text, get_steps_and_ask_sleep_duration)],
            SLEEP_DURATION_ASKED: [MessageHandler(Filters.text, get_sleep_duration_and_ask_fatigue)],

            FATIGUE_ASKED: [MessageHandler(Filters.regex('^(yes|no)$'), get_fatigue_and_ask_concentration)],
            CONCENTRATION_ASKED: [MessageHandler(Filters.regex('^(high|mild|weak|none)$'), get_concentration_and_summarize)],

            DONE: [
                CommandHandler('check', start_and_ask_heart_rate),
                CommandHandler('done', done_start_info),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
