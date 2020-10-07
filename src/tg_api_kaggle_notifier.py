import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue
import datetime
from storage import ChatIdsStorage
from competitions_updater import CompetitionUpdater


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def read_config(token_file='tg_config.json'):
    with open(token_file) as json_file:
        data = json.load(json_file)
        return data


config = read_config()
chat_storage = ChatIdsStorage(config['chats_storage'])
competitionUpdater = CompetitionUpdater(datetime.datetime.now() - datetime.timedelta(1))
update_time = config['update_time'] # hh:mm


def help_command(update, context):
    help_msg = ('I\'m helping you to receive new kaggle competitions to begin compete as soon as possible\n'
        'Commands:\n'
        '/subscribe - Subscribe to get new kaggle competitions daily\n'
        '/unsubscribe - Unsubscribe from daily updates\n'
        '/help - print this message again\n'
    )
    update.message.reply_text(help_msg)


def subscribe(update, context):
    chat = update.message.chat
    chat_storage.add(chat)
    logger.debug('chat subscribed: {}'.format(chat.id))
    update.message.reply_text('Subscribed. Updates will be posted every day after {} msk'.format(update_time))


def unsubscribe(update, context):
    chat_id = update.message.chat_id
    chat_storage.remove(chat_id)
    logger.debug('chat unsubscribed: {}'.format(chat_id))
    update.message.reply_text('Unsubscribed')


def form_message(competitions):
    def form_competition_msg(c, idx):
        msg = ('[{idx}] {id}\n'
              '    title: {title}\n'
              '    category: {category}\n'
              '    days before deadline: {days_before_deadline}\n'
              '    tags: {tags}\n'
              '    url: {url}').format(idx=idx, **c)
        return msg

    return '\n'.join([form_competition_msg(c, idx) for idx, c in enumerate(competitions, start=1)])


def send_competitions_updates(context):
    logger.debug('starting daily updates task')
    query_date = datetime.datetime.now()
    new_competitions = competitionUpdater.get_new_competitions(query_date)
    msg_to_send = form_message(new_competitions)
    logger.debug('get new competitions: {}, query_date: {}'.format(len(new_competitions), query_date))
    if not msg_to_send:
        return
    for chat_id in chat_storage.get_chat_ids():
        context.bot.send_message(chat_id=chat_id, text=msg_to_send, disable_web_page_preview=True)
    logger.debug('sent competitions to chats: {}'.format(len(chat_storage.get_chat_ids())))


def get_daily_time():
    hh, mm = map(int, update_time.split(':'))
    hh = (hh - 3) % 24
    return datetime.time(hour = hh, minute = mm)


def main():
    updater = Updater(config['token'], use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("subscribe", subscribe,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unsubscribe", unsubscribe, pass_chat_data=True))

    updater.start_polling()
    j = updater.job_queue
    j.run_daily(send_competitions_updates, time = get_daily_time())

    updater.idle()


if __name__ == '__main__':
    main()
