import urllib.request
import json
import re

from authlib import auth
from vcardlib import vcard_gen


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
        .format(mobile[0:2], mobile[2:5], mobile[5:8],  mobile[8:10], mobile[10:])
    return formed_mobile


def extract_correct_mobiles(raw_users):
    """
    Получает список спарсенных телефонов,
    выводит список корректных, отформатированных телефонов
    """
    contacts = []
    for user in raw_users:
        phone_number = parse_mobile(user[2])
        if phone_number:
            user[2] = phone_number
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
                raw_users.append([user["last_name"],
                                  user["first_name"],
                                  user["mobile_phone"]])
    return raw_users


def get_friends(auth_data):
    """
    по данным авторизации запрашивает список друзей пользователя
    выводит объект json с данными друзей
    """
    vk_id = auth_data[0]
    token = auth_data[1]
    url = "https://api.vk.com/method/friends.get?user_id=" + \
          vk_id + \
          "&fields=contacts&lang=en&version=5.45" + \
          "&access_token=" + token
    response = urllib.request.urlopen(url).read().decode()
    parsed_json = json.loads(response)
    return parsed_json


def contacts_aggregator():
    auth_data = auth(5333691, "friends", debug=True)

    if len(auth_data) == 0:
        print("Авторизация не удалась")
        exit()
    print("Вы успешно авторизовались!")

    parsed_json = get_friends(auth_data)
    raw_users = filter_by_mobile(parsed_json)
    contacts = extract_correct_mobiles(raw_users)

    if len(contacts) > 0:
        vcard_gen(contacts[0], new=True)
        for contact in contacts[1:]:
            vcard_gen(contact)
        print("Найдено {} валидных контактов у {} друзей!"
              .format(len(contacts), len(raw_users)))


if __name__ == '__main__':
    contacts_aggregator()
