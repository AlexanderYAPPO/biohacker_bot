import datetime
import logging
from pathlib import Path

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from biohack_questions.src import mongoclient
from biohack_questions.src.constants import FILE_DOWNLOAD_PATH
from biohack_questions.src.mongoclient import get_program_by_user

DONE = 'DONE'
SATISFACTION_ASKED = 'SATISFACTION_ASKED'
EFFICIENCY_ASKED = 'EFFICIENCY_ASKED'
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
HRV_ASKED = 'HRV_ASKED'
STEPS_ASKED = 'STEPS_ASKED'
HEART_RATE_ASKED = 'HEART_RATE_ASKED'
PULSE_ASKED = 'PULSE_ASKED'
HRV_BEFORE_MEDITATION_ASKED = 'HRV_BEFORE_MEDITATION_ASKED'
HRV_AFTER_MEDITATION_ASKED = 'HRV_AFTER_MEDITATION_ASKED'

CONVERSATION_TIMEOUT = 3600

logger = logging.getLogger(__name__)


def generate_download_photo_path(update, metric_name):
    file_name = '_'.join([metric_name, update.message.from_user.username, str(datetime.datetime.now())]) + '.jpg'
    return str(FILE_DOWNLOAD_PATH / Path(file_name))


def download_file(bot, update, metric_name):
    file_id = update.message.photo[-1].file_id
    new_file = bot.getFile(file_id)
    file_name = generate_download_photo_path(update, metric_name)
    new_file.download(file_name)
    return file_name


def start_and_ask_heart_rate(update, context):
    update.message.reply_text('Загрузите скриншот с показаниями сердечного ритма с вашего фитнесс трекера. Замеряйте в положении стоя в состоянии покоя.')
    return HEART_RATE_ASKED


def get_heart_rate_and_ask_steps(update, context):
    file_name = download_file(context.bot, update, 'heart_rate')
    context.user_data['heart_rate'] = file_name
    update.message.reply_text('Загрузите скриншот с количеством пройденных шагов за день с вашего фитнесс трекера')
    return STEPS_ASKED


def get_steps_and_ask_hrv(update, context):
    file_name = download_file(context.bot, update, 'steps')
    context.user_data['steps'] = file_name
    update.message.reply_text('Загрузите скриншот с показаниями HRV. Замеряйте в положении стоя в состоянии покоя.')
    return HRV_ASKED


def get_hrv_and_ask_sleep_duration(update, context):
    file_name = download_file(context.bot, update, 'hrv')
    context.user_data['hrv'] = file_name
    update.message.reply_text('Напишите сколько часов вы сегодня спали?')
    return SLEEP_DURATION_ASKED


def get_sleep_duration_and_ask_bed_time(update, context):
    value = update.message.text
    context.user_data['hours_of_sleep'] = value

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text('Вы легли спать до 12?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
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
    update.message.reply_text('Проверьте свою скорость реакции. Пройдите тест по ссылке https://humanbenchmark.com/tests/reactiontime и загрузите '
                              'скриншот с результатами')
    return REACTION_TEST_ASKED


def get_reaction_test_and_ask_activity_duration(update, context):
    file_name = download_file(context.bot, update, 'reaction')
    context.user_data['reaction'] = file_name
    reply_keyboard = [['сегодня тренировки не было', 'до 30 мин', '30-60 минут', '60-90 минут', 'более 90 минут']]
    update.message.reply_text('сколько вы сегодня занимались физической активностью?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ACTIVITY_DURATION_ASKED


def get_activity_duration_and_ask_activity_level_or_breakfast(update, context):
    value = update.message.text
    context.user_data['activity_duration'] = value
    if value == 'сегодня тренировки не было':
        update.message.reply_text('Укажите приблизительное время первого приема пищи')
        return BREAKFAST_TIME_ASKED
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


def get_meetings_and_ask_efficiency(update, context):
    value = update.message.text
    context.user_data['meetings'] = value

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text('Выполнили ли вы все запланированные на сегодня задачи.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return EFFICIENCY_ASKED


def get_efficiency_and_ask_satisfaction(update, context):
    value = update.message.text
    context.user_data['efficiency'] = value

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text('Довольны ли вы своей эффективностью сегодня.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SATISFACTION_ASKED


def get_satisfaction_and_ask_comments(update, context):
    value = update.message.text
    context.user_data['satisfaction'] = value

    update.message.reply_text('поделитесь общим комментарием к сегодняшнему дню, было ли что то необычное, чувствовали ли вы себя лучше или хуже? (высокая '
                              'температура, очень интенсивная спортивная нагрузка, долгие перелет, стрессовое событие).')
    return COMMENTS_ASKED


def select_program_specific_path(update, context):
    program = get_program_by_user(update.message.from_user.username)
    if program is not None and program == 'sport':
        if context.user_data['activity_duration'] == 'сегодня тренировки не было':
            update.message.reply_text('Введите /check чтобы перезаполнить или /done чтобы завершить опрос')
            return DONE
        update.message.reply_text('Отправьте скриншот изменений пульса во время тренировки')
        return PULSE_ASKED
    if program is not None and program == 'meditation':
        update.message.reply_text('Загрузите скриншот с показаниями HRV до медитации')
        return HRV_BEFORE_MEDITATION_ASKED
    update.message.reply_text('Введите /check чтобы перезаполнить или /done чтобы завершить опрос')
    return DONE


def get_comments_and_continue_by_program(update, context):
    value = update.message.text
    context.user_data['comments'] = value
    return select_program_specific_path(update, context)


def get_pulse_and_summarize(update, context):
    file_name = download_file(context.bot, update, 'pulse')
    context.user_data['pulse'] = file_name
    update.message.reply_text('Введите /check чтобы перезаполнить или /done чтобы завершить опрос')
    return DONE


def get_hrv_before_meditation_and_ask_hrv_after_meditation(update, context):
    file_name = download_file(context.bot, update, 'hrv_before_meditation')
    context.user_data['hrv_before_meditation'] = file_name
    update.message.reply_text('Загрузите скриншот с показаниями HRV после медитации')
    return HRV_AFTER_MEDITATION_ASKED


def get_hrv_after_meditation_and_summarize(update, context):
    file_name = download_file(context.bot, update, 'hrv_after_meditation')
    context.user_data['hrv_after_meditation'] = file_name
    update.message.reply_text('Введите /check чтобы перезаполнить или /done чтобы завершить опрос')
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
        'breakfast_time': context.user_data['breakfast_time'],
        'dinner_time': context.user_data['dinner_time'],
        'meetings': context.user_data['meetings'],
        'comments': context.user_data['comments'],

        'activity_level': context.get('activity_level'),

        'pulse': context.get('pulse'),

        'hrv_before_meditation': context.get('hrv_before_meditation'),
        'hrv_after_meditation': context.get('hrv_after_meditation'),
    }
    mongoclient.add_log_record(log_record_dict)
    update.message.reply_text('Опрос окончен, спасибо.')
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Диалог отменен. Введите /start чтобы заполнить стартовую анкету или /check чтобы сообщить результаты сегодняшних показаний.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def timeout(update, context):
    update.message.reply_text("Ответ не был получен за отведенное время. Наберите /check для повторной попытки")
    return ConversationHandler.END


def generate_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('check', start_and_ask_heart_rate)],
        states={
            HEART_RATE_ASKED: [MessageHandler(Filters.photo, get_heart_rate_and_ask_steps)],
            STEPS_ASKED: [MessageHandler(Filters.photo, get_steps_and_ask_hrv)],
            HRV_ASKED: [MessageHandler(Filters.photo, get_hrv_and_ask_sleep_duration)],
            SLEEP_DURATION_ASKED: [MessageHandler(Filters.text, get_sleep_duration_and_ask_bed_time)],
            BED_TIME_ASKED: [MessageHandler(Filters.regex('^(Да|Нет)$'), get_bed_time_and_ask_fatigue)],
            FATIGUE_ASKED: [MessageHandler(Filters.regex('^(Да|Нет)$'), get_fatigue_ask_reaction_test)],
            REACTION_TEST_ASKED: [MessageHandler(Filters.photo, get_reaction_test_and_ask_activity_duration)],
            ACTIVITY_DURATION_ASKED: [
                MessageHandler(Filters.regex('^(сегодня тренировки не было|до 30 мин|30-60 минут|60-90 минут|более 90 минут)$'), get_activity_duration_and_ask_activity_level_or_breakfast)],
            ACTIVITY_LEVEL_ASKED: [MessageHandler(Filters.regex('^(высокая|средняя|лёгкая)$'), get_activity_level_and_ask_breakfast_time)],
            BREAKFAST_TIME_ASKED: [MessageHandler(Filters.text, get_breakfast_time_and_ask_dinner_time)],
            DINNER_TIME_ASKED: [MessageHandler(Filters.text, get_dinner_time_and_ask_meetings)],
            MEETINGS_ASKED: [
                MessageHandler(Filters.regex('^(да, меньше 1 часа|да, более 1 часа|нет)$'), get_meetings_and_ask_efficiency)],
            EFFICIENCY_ASKED: [MessageHandler(Filters.regex('^(Да|Нет)$'), get_efficiency_and_ask_satisfaction)],
            SATISFACTION_ASKED: [MessageHandler(Filters.regex('^(Да|Нет)$'), get_satisfaction_and_ask_comments)],
            COMMENTS_ASKED: [MessageHandler(Filters.text, get_comments_and_continue_by_program)],
            PULSE_ASKED: [MessageHandler(Filters.photo, get_pulse_and_summarize)],
            HRV_BEFORE_MEDITATION_ASKED: [MessageHandler(Filters.photo, get_hrv_before_meditation_and_ask_hrv_after_meditation)],
            HRV_AFTER_MEDITATION_ASKED: [MessageHandler(Filters.photo, get_hrv_after_meditation_and_summarize)],
            DONE: [
                CommandHandler('check', start_and_ask_heart_rate),
                CommandHandler('done', done_start_info),
            ],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.all, timeout)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=CONVERSATION_TIMEOUT,
    )
