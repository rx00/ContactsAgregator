import json
import re
import os
import sys
import logging
import urllib.request

from importlib.util import find_spec

from utils.authutils import text_caller
from authlibs.vklib import VkApi
from vcardlib import Card

from authdata import get_vk_token
from authdata import write_vk_token


def init_logger(debug=False):
    """
    главный логгер
    """
    if debug:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.CRITICAL

    logging.basicConfig(format="[%(filename)s] [%(asctime)s] %(message)s",
                        level=debug_level,
                        filename="debug.log")


def parse_mobile(raw_mobile):
    """
    Получает строку, предположительно содержащую мобильный телефон
    номер проходит ряд проверок (длинна, префикс)
    на выход посылается либо пустая строка, либо отформатированный
    мобильный телефон
    """
    parts = re.findall(r'\d*', raw_mobile)
    mobile = ''.join(parts)
    if len(mobile) > 11 or len(mobile) < 10:
        return ""
    if len(mobile) == 10:
        mobile = "+7" + mobile
    elif len(mobile) == 11:
        mobile = "+7" + mobile[1:]
    formed_mobile = "{} ({}) {}-{}-{}"\
        .format(mobile[0:2],
                mobile[2:5],
                mobile[5:8],
                mobile[8:10],
                mobile[10:])
    return formed_mobile


def extract_correct_mobiles(raw_users):
    """
    Получает список спарсенных телефонов,
    выводит список корректных, отформатированных телефонов
    """
    contacts = []
    for user in raw_users:
        mobile_phone = parse_mobile(user["mobile_phone"])
        if mobile_phone:
            user["mobile_phone"] = mobile_phone
            contacts.append(user)
    return contacts


def filter_by_mobile(parsed_json):
    """
    по полученному json объекту ищет мобильные телефоны
    выводит список [фамилия, имя, телефон]
    """
    raw_users = []
    for user in parsed_json["response"]:
        if "mobile_phone" in user:
            if user["mobile_phone"] != "":
                raw_users.append({"vk_id": user["user_id"],
                                  "domain": user["domain"],
                                  "photo_50": user["photo_50"],
                                  "last_name": user["last_name"],
                                  "first_name": user["first_name"],
                                  "mobile_phone": user["mobile_phone"]})
    return raw_users


def get_friends(auth_data):  # TODO забросить в vklib
    """
    по данным авторизации запрашивает список друзей пользователя
    выводит объект json с данными друзей
    """
    vk_id = auth_data.id
    token = auth_data.token
    url = "https://api.vk.com/method/friends.get?user_id=" + \
          vk_id + \
          "&fields=domain,contacts,photo_50&lang=en&version=5.45" + \
          "&access_token=" + token
    response = urllib.request.urlopen(url).read().decode()
    parsed_json = json.loads(response)

    if "error" in parsed_json:
        return {}
    else:
        return parsed_json


def run_vk_auth():
    """
    главный авторизатор ВКонтакте
    """
    auth_resources = {
        "permissions": "friends",
        "client_id": 5333691
    }

    crypto_factor = find_spec("Crypto")
    found = crypto_factor is not None

    bad_token = True
    key = ""

    if found:
        if not os.path.isfile("data"):
            print("Для начала работы с программой, придумайте свой пароль,\n"
                  "ваши данные для авторизации!")
        key = text_caller("Master-key")
        vk_data = get_vk_token(key)
        if "token" in vk_data:
            auth_resources["token"] = vk_data["token"]
            auth_resources["id"] = vk_data["id"]
            bad_token = False
            logging.debug("Old data mined, vk session still alive!")
    else:
        print("Библиотека Crypto не найдена!\n"
              "Сохранение данных авторизации не поддерживается!")

    auth_data = VkApi(auth_resources)

    if found:
        if bad_token:
            write_vk_token(auth_data.token, auth_data.id, key, 86400)
    if auth_data.token == "":
        print("Авторизация не удалась")
        exit()
    print("Вы успешно авторизовались!")
    return auth_data


def contacts_aggregator(card_file="cards.vcf"):  # TODO бросить в аргументы файл карт
    print("===> Экспорт адресной книги <===")
    logging.debug("===> Application started <===")

    auth_data = run_vk_auth()
    parsed_json = get_friends(auth_data)

    if len(parsed_json) == 0:
        auth_resourses = {
            "permissions": "friends",
            "client_id": 5333691
        }
        auth_data = VkApi(auth_resourses)
        parsed_json = get_friends(auth_data)

    raw_users = filter_by_mobile(parsed_json)
    contacts = extract_correct_mobiles(raw_users)
    print("Найдено {} валидных контактов у {} друзей!"
          .format(len(contacts), len(raw_users)))

    card_list = []
    if len(contacts) > 0:
        for contact in contacts:
            card_list.append(Card(contact))
        try:
            with open(card_file, "w") as card_storage:
                i = 1
                for card in card_list:
                    card_storage.write(str(card))
                    print("[{}/{}] Контакт {} {} создан".format(
                        i, len(contacts), card.last_name_en, card.first_name_en
                    ))
                    i += 1
        except OSError:
            print("Программа не может получить доступ к файлу {}!"
                  .format(card_file))
    else:
        print("Ваши друзья не хотят делиться мобильными телефонами ;(")


if __name__ == '__main__':
    debug = False
    if len(sys.argv) > 1:
        if "--help" in sys.argv:
            print("====> Генератор адресной книги <====\n"
                  "В данный момент, программа не нуждается в\n"
                  "дополнительных аргументах.\n"
                  "Запуск: python3 {}\n"
                  "Программе требуются права на запись в папку"
                  .format(sys.argv[0]))
            exit()
        elif "--debug" in sys.argv:
            debug = True
            print("Программа запущена в режиме дебага!")
    init_logger(debug)
    contacts_aggregator()
