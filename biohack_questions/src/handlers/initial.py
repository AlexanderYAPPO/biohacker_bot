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
    update.message.reply_text('Здравствуйте! Это бот помощник которому вы будете отправлять ежедневные данные о своей активности. Напишите, как вас зовут.')
    return PROVIDE_NAME


def provide_name(update, context):
    user_name = update.message.text
    user = update.message.from_user

    context.user_data['name'] = user_name

    update.message.reply_text('Напишите свою дату рождения в формате "YYYY-MM-DD".')

    return PROVIDE_DOB


def provide_dob(update, context):
    user_dob = update.message.text

    try:
        context.user_data['date_of_birth'] = datetime.datetime.strptime(user_dob, '%Y-%m-%d')
    except ValueError:
        update.message.reply_text('Вы ввели дату в неверном формате. Например, если дата рождения 12 Мая 1990 то введите 1990-05-12. Попробуйте снова.')
        return PROVIDE_DOB

    reply_keyboard = [['Спорт', 'Диета', 'Медитация']]

    update.message.reply_text(
        'Напишите, какую активность вам выбрали во время исследования.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECT_PROGRAM


def select_program(update, context):

    program_remapping = {
        'Спорт': 'sport',
        'Диета': 'diet',
        'Медитация': 'meditation',
    }
    program = program_remapping.get(update.message.text, 'unknown')

    context.user_data['program'] = program

    update.message.reply_text('Анкета заполнена. Если все заполнено верно - введите /done. Если хотите перезаполнить - введите /start')

    return DONE


def done_start_info(update, context):
    user_dict = {
        'username': update.message.from_user.username,
        'name': context.user_data['name'],
        'date_of_birth': context.user_data['date_of_birth'],
        'program': context.user_data['program'],
    }
    mongoclient.add_user_info(user_dict)

    update.message.reply_text('Мы запомнили ваши данные. Мы просим заполнять опросник об активности каждый день. Для этого вам нужно будет вводить команду '
                              '/check которая запускает опросник. Ваши ежедневные показания очень важны для исследования. Постарайтесь не пропускать дни '
                              'заполнения. По умолчанию мы будем напоминать вам об опроснике каждый день в это время. Если вам не хочется получать '
                              'напоминания, введите /unset_reminder. Если же вы передумали и наоборот хотите снова начать получать уведомления, '
                              'введите /set_reminder')
    set_reminder(update, context)
    
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Диалог отменен. Введите /start чтобы заполнить стартовую анкету или /check чтобы сообщить результаты сегодняшних показаний.',
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
            SELECT_PROGRAM: [MessageHandler(Filters.regex('^(Спорт|Диета|Медитация])$'), select_program)],
            DONE: [
                CommandHandler('start', start),
                CommandHandler('done', done_start_info),
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.all, timeout)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    )
