import re


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