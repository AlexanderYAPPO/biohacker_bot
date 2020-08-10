from telegram.ext import CommandHandler


def ping_user(context):
    job = context.job
    context.bot.send_message(job.context, text='A daily reminder to send your data. Type /check')


def set_reminder(update, context):
    new_job = context.job_queue.run_repeating(ping_user, 3600 * 24, context=update.message.chat_id)
    context.chat_data['job'] = new_job
    update.message.reply_text('All set, we will be asking you to provide some information every day. Type /unset_reminder to stop the reminder')


def unset_reminder(update, context):
    if 'job' not in context.chat_data:
        update.message.reply_text('The reminder is already stopped')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('The reminder has been stopped')


def generate_set_handler():
    return CommandHandler('set_reminder', set_reminder)


def generate_unset_handler():
    return CommandHandler('unset_reminder', unset_reminder)
