import datetime
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from biohack_questions.src import mongoclient

DONE = 'DONE'
COMMENTS_ASKED = 'COMMENTS_ASKED'
MEETINGS_ASKED = 'MEETINGS_ASKED'
DINNER_TIME_ASKED = 'DINNER_TIME_ASKED'
BREAKFAST_TIME_ASKED = 'BREAKFAST_TIME_ASKED'
ACTIVITY_LEVEL_ASKED = 'ACTIVITY_LEVEL_ASKED'
ACTIVITY_DURATION_ASKED = 'ACTIVITY_DURATION_ASKED'
REACTION_TEST_ASKED = 'REACTION_TEST_ASKED'
FATIGUE_ASKED = 'FATIGUE_ASKED'
BED_TIME_ASKED = 'BED_TIME_ASKED'
SLEEP_DURATION_ASKED = 'SLEEP_DURATION_ASKED'
STEPS_ASKED = 'STEPS_ASKED'
HEART_RATE_ASKED = 'HEART_RATE_ASKED'

logger = logging.getLogger(__name__)


def start_and_ask_heart_rate(update, context):
    update.message.reply_text('Укажите показания сердечного ритма')
    return HEART_RATE_ASKED


def get_heart_rate_and_ask_steps(update, context):
    value = update.message.text
    context.user_data['heart_rate'] = value
    update.message.reply_text('Укажите количество пройденных шагов за день')
    return STEPS_ASKED


def get_steps_and_ask_sleep_duration(update, context):
    value = update.message.text
    context.user_data['steps'] = value
    update.message.reply_text('Напишите сколько часов вы сегодня спали?')
    return SLEEP_DURATION_ASKED


def get_sleep_duration_and_ask_bed_time(update, context):
    value = update.message.text
    context.user_data['hours_of_sleep'] = value

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text('Вы легли спать до 12? варианты ответов', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BED_TIME_ASKED


def get_bed_time_and_ask_fatigue(update, context):
    value = update.message.text
    context.user_data['bed_time_before_12'] = value

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text('Чувствуете ли вы усталость?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return FATIGUE_ASKED


def get_fatigue_ask_reaction_test(update, context):
    value = update.message.text
    context.user_data['fatigue'] = value
    update.message.reply_text('Проверьте свою скорость реакции. Пройдите тест по ссылке https://www.justpark.com/creative/reaction-time-test/ и укажите '
                              'результат в милисекундах')
    return REACTION_TEST_ASKED


def get_reaction_test_and_ask_activity_duration(update, context):
    value = update.message.text
    try:
        value = int(value)
    except ValueError:
        pass

    context.user_data['reaction'] = value
    reply_keyboard = [['до 30 мин', '30-60 минут', '60-90 минут', 'более 90 минут']]
    update.message.reply_text('сколько вы сегодня занимались физической активностью?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ACTIVITY_DURATION_ASKED


def get_activity_duration_and_ask_activity_level(update, context):
    value = update.message.text
    context.user_data['activity_duration'] = value
    reply_keyboard = [['высокая', 'средняя', 'лёгкая']]
    update.message.reply_text('как вы оцениваете активность физической тренировки', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ACTIVITY_LEVEL_ASKED


def get_activity_level_and_ask_breakfast_time(update, context):
    value = update.message.text
    context.user_data['activity_level'] = value
    update.message.reply_text('Укажите приблизительное время первого приема пищи')
    return BREAKFAST_TIME_ASKED


def get_breakfast_time_and_ask_dinner_time(update, context):
    value = update.message.text
    context.user_data['breakfast_time'] = value
    update.message.reply_text('Укажите приблизительное время последнего приема пищи')
    return DINNER_TIME_ASKED


def get_dinner_time_and_ask_meetings(update, context):
    value = update.message.text
    context.user_data['dinner_time'] = value

    reply_keyboard = [['да, меньше 1 часа', 'да, более 1 часа', 'нет']]
    update.message.reply_text('были ли у вас активные онлайн совещания (zoom) в течение дня',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return MEETINGS_ASKED


def get_meetings_and_ask_comments(update, context):
    value = update.message.text
    context.user_data['meetings'] = value
    update.message.reply_text('поделитесь общим комментарием к сегодняшнему дню, было ли что то необычное , чувствовали ли вы себя лучше или хуже ?')
    return COMMENTS_ASKED


def get_comments_and_summarize(update, context):
    value = update.message.text
    context.user_data['comments'] = value
    update.message.reply_text('Вот что вы сообщили: %s. Нажмите /check чтобы перезаполнить и /done чтобы завершить опрос' % context.user_data)
    return DONE


def done_start_info(update, context):
    log_record_dict = {
        'username': update.message.from_user.username,
        'date': datetime.datetime.now(),

        'heart_rate': context.user_data['heart_rate'],
        'steps': context.user_data['steps'],
        'hours_of_sleep': context.user_data['hours_of_sleep'],
        'bed_time_before_12': context.user_data['bed_time_before_12'],
        'fatigue': context.user_data['fatigue'],
        'reaction': context.user_data['reaction'],
        'activity_duration': context.user_data['activity_duration'],
        'activity_level': context.user_data['activity_level'],
        'breakfast_time': context.user_data['breakfast_time'],
        'dinner_time': context.user_data['dinner_time'],
        'meetings': context.user_data['meetings'],
        'comments': context.user_data['comments'],
    }
    mongoclient.add_log_record(log_record_dict)
    update.message.reply_text('Опрос окончен, спасибо.')
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
            HEART_RATE_ASKED: [MessageHandler(Filters.text, get_heart_rate_and_ask_steps)],
            STEPS_ASKED: [MessageHandler(Filters.text, get_steps_and_ask_sleep_duration)],
            SLEEP_DURATION_ASKED: [MessageHandler(Filters.text, get_sleep_duration_and_ask_bed_time)],
            BED_TIME_ASKED: [MessageHandler(Filters.regex('^(Да|Нет)$'), get_bed_time_and_ask_fatigue)],
            FATIGUE_ASKED: [MessageHandler(Filters.regex('^(Да|Нет)$'), get_fatigue_ask_reaction_test)],
            REACTION_TEST_ASKED: [MessageHandler(Filters.text, get_reaction_test_and_ask_activity_duration)],
            ACTIVITY_DURATION_ASKED: [
                MessageHandler(Filters.regex('^(до 30 мин|30-60 минут|60-90 минут|более 90 минут)$'), get_activity_duration_and_ask_activity_level)],
            ACTIVITY_LEVEL_ASKED: [MessageHandler(Filters.regex('^(высокая|средняя|лёгкая)$'), get_activity_level_and_ask_breakfast_time)],
            BREAKFAST_TIME_ASKED: [MessageHandler(Filters.text, get_breakfast_time_and_ask_dinner_time)],
            DINNER_TIME_ASKED: [MessageHandler(Filters.text, get_dinner_time_and_ask_meetings)],
            MEETINGS_ASKED: [
                MessageHandler(Filters.regex('^(да, меньше 1 часа|да, более 1 часа|нет)$'), get_meetings_and_ask_comments)],
            COMMENTS_ASKED: [MessageHandler(Filters.text, get_comments_and_summarize)],

            DONE: [
                CommandHandler('check', start_and_ask_heart_rate),
                CommandHandler('done', done_start_info),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
