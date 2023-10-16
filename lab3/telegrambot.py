import telebot
from threading import Lock
from geocoding import geocoding
from weather import get_weather
from opentripmap import get_object_list, get_object_properties
from bs4 import BeautifulSoup

mutex = Lock()
help_msg = ("Этот телеграм бот умеет "
            "показывать интересные вещи, которые "
            "можно получить по названию локации!\n"
            "Просто введи название!")

GEOCODING_LIMIT = 7
OPENTRIPMAP_LIMIT = 5
OTM_RADIUS = 10000
OTM_LIMIT = 5


TOKEN = "6279295910:AAGkwcUbRgIJgt9y1xMBZRnRBTxbUpV0l4U"
bot = telebot.TeleBot(TOKEN)
session = {}


def reply_first(message):
    data = geocoding(message.text, GEOCODING_LIMIT)
    with mutex:
        session[message.chat.id] = {
            'geocoding': dict(data)
        }
    bot.send_message(message.chat.id, "Вот найденные локации:")
    msg = ""
    for i, place in enumerate(data['hits']):
        msg += (f"{i+1}) {place['name']}, "
                f"{place['city'] if 'city' in place.keys() else '-'}, "
                f"{place['state'] if 'state' in place.keys() else '-'}, "
                f"{place['country'] if 'country' in place.keys() else '-'}\n")
    if msg:
        bot.send_message(message.chat.id, msg)
        bot.send_message(message.chat.id, "Выберите локацию по номеру:")   
    else:
        with mutex:
            bot.send_message(message.chat.id, "Локаций не найдено")
            del session[message.chat.id]
            return


def reply_second(message):
    try:
        choose = int(message.text)
        with mutex:
            count = len(session[message.chat.id]['geocoding']['hits'])
        if choose < 1 or choose > count:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный номер >:(")
        return
    
    with mutex:
        data = dict(session[message.chat.id])
    point = data['geocoding']['hits'][choose-1]['point']
    lat, lon = point['lat'], point['lng']
    object_list_data = get_object_list(lat, lon, OTM_RADIUS, OTM_LIMIT)
    object_xid = [feature['properties']['xid'] for feature in object_list_data['features']]
    object_properties = [get_object_properties(xid) for xid in object_xid]
    # for prop in object_properties:
    #     bot.send_message(message.chat.id, str(prop))
    object_description = [{
        'name': prop['name'],
        'otm': prop['otm'],
        'desc': prop['info']['descr'] if 'info' in prop.keys() else "Отсутствует",
        'src': prop['info']['src'] if 'info' in prop.keys() else "Отсутствует"
    } for prop in object_properties]

    bot.send_message(message.chat.id, "Вот какие интересные мета мне удалось найти:")
    for obj in object_description:
        msg = obj['name']
        msg += "\nОписание: " + BeautifulSoup(obj['desc'], features="lxml").getText("\n") + "\n"
        msg += "Официальный сайт: " + obj['src'] + "\n"
        msg += "Страница на opentripmap: " + obj['otm']
        bot.send_message(message.chat.id, msg)
    bot.send_message(message.chat.id, "Надеюсь, тебе было интересно!")

    with mutex:
        del session[message.chat.id]


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! " + help_msg)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.chat.id in session.keys():
        reply_second(message)
    else:
        reply_first(message)

try:
    bot.infinity_polling()
except KeyboardInterrupt:
    bot.stop_bot()
