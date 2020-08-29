import datetime
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from biohack_questions.src import mongoclient
from biohack_questions.src.handlers.reminder import set_reminder

logger = logging.getLogger(__name__)


PROVIDE_NAME = 'PROVIDE_NAME'
PROVIDE_DOB = 'PROVIDE_DOB'
SELECT_PROGRAM = 'SELECT_PROGRAM'
DONE = 'DONE'

CONVERSATION_TIMEOUT = 3600


def start(update, context):
    # reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text('Tell me your name')

    return PROVIDE_NAME


def provide_name(update, context):
    user_name = update.message.text
    user = update.message.from_user

    context.user_data['name'] = user_name

    update.message.reply_text('User %s responded with a name %s. Now tell me your date of birth in the following format: "YYYY-MM-DD".'
                              % (user.username, user_name))

    return PROVIDE_DOB


def provide_dob(update, context):
    user_dob = update.message.text

    try:
        context.user_data['date_of_birth'] = datetime.datetime.strptime(user_dob, '%Y-%m-%d')
    except ValueError:
        update.message.reply_text('You used an incorrect format. For example, 12 May 1990 will be 1990-05-12. Try again.')
        return PROVIDE_DOB

    reply_keyboard = [['fitness', 'diet', 'mindfulness', 'control']]

    update.message.reply_text(
        'Your date of birth is %s. Now select the program you\'re enrolled to',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECT_PROGRAM


def select_program(update, context):
    context.user_data['program'] = update.message.text

    update.message.reply_text('This is what we have now %s. Type /start to re-fill the data or /done to finish' % context.user_data)

    return DONE


def done_start_info(update, context):
    user_dict = {
        'username': update.message.from_user.username,
        'name': context.user_data['name'],
        'date_of_birth': context.user_data['date_of_birth'],
        'program': context.user_data['program'],
    }
    mongoclient.add_user_info(user_dict)

    set_reminder(update, context)
    
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def timeout(update, context):
    update.message.reply_text("Ответ не был получен за отведенное время. Наберите /start для повторной попытки")
    return ConversationHandler.END


def generate_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROVIDE_NAME: [MessageHandler(Filters.text, provide_name)],
            PROVIDE_DOB: [MessageHandler(Filters.text, provide_dob)],
            SELECT_PROGRAM: [MessageHandler(Filters.regex('^(fitness|control|mindfulness|diet)$'), select_program)],
            DONE: [
                CommandHandler('start', start),
                CommandHandler('done', done_start_info),
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.all, timeout)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    )
