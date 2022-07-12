# inbuilt helper library
import sys
import time

"""
    * A simple, but extensible Python implementation for the Telegram Bot API. 
    * visit: https://github.com/eternnoir/pyTelegramBotAPI
"""
import telebot
from telebot import types

"""
    * Google Custom Search Api.
    * visit: https://developers.google.com/custom-search/docs/element
"""
from googleapiclient.discovery import build

import ApiKeys  # helper python file, contains all secret keys required in the project 


bot = telebot.TeleBot(ApiKeys.SEARCH_BOT_API_TOKEN)  # initialization of bot
service = build("customsearch", "v1", developerKey=ApiKeys.CUSTOM_SEARCH_TOKEN) # intialization of Google Custom Search service


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
        * Welcome Message of the bot.
        * works for /start and /help command
    """
    bot.reply_to(message, u"Hello, welcome to THE SEARCH BOT \
                            \n You can search anything and everything via me. \
                            \n Simply use @thesearchbot in your chat box to ask queries")


@bot.inline_handler(lambda query: len(query.query) > 3)
def query_text(inline_query):
    """
        * responds to inline query of the bot.
        * working:
        *       First retrieve the query
        *       Search via Google Custom Search service
        *       Store the results
        *       Show formatted output
        :param inline_query: query used by the user in inline chat
        :return: List of top 5 results for the given query
    """
    response = []  # store list of responses from the server
    try:

        results = service.cse().list(q=inline_query.query, cx=ApiKeys.CSE_ID).execute()  # fetch result for the query.

        if results:
            # if result is found for the query

            resp = types.InlineQueryResultArticle('1', 'Top Results',
                                                  types.InputTextMessageContent('Top 5 Results: '))
            response.append(resp)
            item = results.get('items')

            for i in range(0, 5, 1):
                print(item[i])
                resp = types.InlineQueryResultArticle(str(i+2), item[i]["title"],
                                                      types.InputTextMessageContent(
                                                               '*'+ item[i]["title"] + '*\n'
                                                                + item[i]["snippet"] + '\n'
                                                                + '[View More]('+item[i]['link']+') ', parse_mode='Markdown'),
                                                      url=item[i]['link'],
                                                      description=item[i]['snippet'][:100])
                response.append(resp)
        else:
            resp = types.InlineQueryResultArticle('1', 'Sorry I did\'t get you. Would you please simplify your query?',
                                                  types.InputTextMessageContent('Search again using @thesearchbot'))
            response.append(resp)
        # print(response, "\n")

    except Exception as e:
        if str(e).__contains__('403'):
            # if daily maximum search result exceeds.
            resp = types.InlineQueryResultArticle('1', 'Sorry Maximum Daily request exceeded',
                                                  types.InputTextMessageContent(
                                                      'Sorry Maximum Daily request exceeded. Search again tomorrow :)'))
        else:
            resp = types.InlineQueryResultArticle('1', 'Sorry I did\'t get you. \n' +
                                                  'try again?',
                                                  types.InputTextMessageContent('Search again using @thesearchbot'))
        response.append(resp)

        print("Exception: ", str(e))
    finally:
        # respond to the inline query
        bot.answer_inline_query(inline_query.id, response, cache_time=1)


def main_loop():
    # keep the bot always online
    bot.polling(True)
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print(sys.stderr, '\nExiting by user request.\n')
        sys.exit(0)
