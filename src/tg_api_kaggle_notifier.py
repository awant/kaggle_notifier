import json
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue
import datetime
from storage import ChatIdsStorage
from competitions_updater import CompetitionUpdater
import os

logging.basicConfig(filename='kaggle_notifier.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def read_config(token_file=os.environ['TG_CONFIG']):
    with open(token_file) as json_file:
        data = json.load(json_file)
        return data


config = read_config()
chat_storage = ChatIdsStorage(config['chats_storage'])
competition_updater = CompetitionUpdater(datetime.datetime.now() - datetime.timedelta(1))
update_time = config['update_time'] # hh:mm


def help_command(update, context):
    help_msg = ('I\'m helping you to receive new kaggle competitions to begin compete as soon as possible\n'
        'Commands:\n'
        '/subscribe - Subscribe to get new kaggle competitions daily\n'
        '/unsubscribe - Unsubscribe from daily updates\n'
        '/state <competition> - Get a current state of the competition\n'
        '/help - Print this message again\n'
    )
    logger.info('chat_id {} requested the help command'.format(update.message.chat.id))
    update.message.reply_text(help_msg)


def subscribe(update, context):
    chat = update.message.chat
    chat_storage.add(chat)
    logger.info('chat id {} requested a subscription'.format(chat.id))
    update.message.reply_text('Subscribed. Updates will be posted every day after {} msk (if there is any)'.format(update_time))


def unsubscribe(update, context):
    chat_id = update.message.chat_id
    chat_storage.remove(chat_id)
    logger.info('chat_id {} requested a cancelling subscription'.format(chat_id))
    update.message.reply_text('Unsubscribed')


def form_state_message(state):
    def parse_leaderboard(leaderboard):
        header = 'place  score  date'
        body = '\n'.join(['{:>5}  {}  {}'.format(numb, x['score'], x['date']) for numb, x in leaderboard])
        return header + '\n' + body

    msg = ('title: {title}\n'
           'reward: {reward}\n'
           'teams count: {teams}\n'
           'days before deadline: {days_before_deadline}\n'
           'evaluation metric: {evaluation_metric}\n'
           'url: {url}').format(**state)

    leaderboard_msg = None
    if len(state['leaderboard']) > 0:
        leaderboard_msg = 'Leaderboard\n```\n{}```'.format(parse_leaderboard(state['leaderboard']))

    return msg, leaderboard_msg


def state(update, context):
    chat_id = update.message.chat_id
    msg_text = update.message.text
    competition_id = msg_text[msg_text.find(' ')+1:]
    logger.info('chat_id {} requested a state for the competition {}'.format(chat_id, competition_id))
    state = competition_updater.get_state(competition_id)
    if isinstance(state, str):
        update.message.reply_text(state)
        return
    state_msg, leaderboard_msg = form_state_message(state)
    update.message.reply_text(state_msg, disable_web_page_preview=True)
    if leaderboard_msg:
        update.message.reply_markdown_v2(leaderboard_msg)


def form_competition_message(competitions):
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
    logger.info('starting a daily updates task')
    query_date = datetime.datetime.now()
    new_competitions = competition_updater.get_new_competitions(query_date)
    msg_to_send = form_competition_message(new_competitions)
    logger.info('get new competitions: {}, query_date: {}'.format(len(new_competitions), query_date))
    if not msg_to_send:
        return
    for chat_id in chat_storage.get_chat_ids():
        context.bot.send_message(chat_id=chat_id, text=msg_to_send, disable_web_page_preview=True)
    logger.info('sent competitions to chats: {}'.format(len(chat_storage.get_chat_ids())))


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
    dp.add_handler(CommandHandler("state", state, pass_chat_data=True))

    updater.start_polling()
    j = updater.job_queue
    j.run_daily(send_competitions_updates, time = get_daily_time())

    updater.idle()


if __name__ == '__main__':
    main()
