from telegram.ext import CommandHandler


def ping_user(context):
    job = context.job
    context.bot.send_message(job.context, text='Привет, это ежедневное напоминание об опроснике. Введите /check чтобы начать заполнение.')


def set_reminder(update, context):
    job = context.chat_data.get('job')
    if job is not None:
        job.schedule_removal()

    new_job = context.job_queue.run_repeating(ping_user, 3600 * 24, context=update.message.chat_id)
    context.chat_data['job'] = new_job


def set_reminder_command(update, context):
    set_reminder(update, context)
    update.message.reply_text('Напоминание установлено. Мы напишем вам через 24 часа. Введите /unset_reminder если вы не хотите больше получать напоминания')


def unset_reminder_command(update, context):
    msg = 'Напоминания отключены. Не забудьте заполнить данные самостоятельно. Если вы хотите снова начать получать напоминания - введите /set_reminder'

    if 'job' not in context.chat_data:
        update.message.reply_text(msg)
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text(msg)


def generate_set_handler():
    return CommandHandler('set_reminder', set_reminder_command)


def generate_unset_handler():
    return CommandHandler('unset_reminder', unset_reminder_command)
