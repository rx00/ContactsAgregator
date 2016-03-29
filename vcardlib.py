def lines_pre_gen():
    """
    Возвращает заготовку карты (списком)
    """
    card = list()
    card.append("BEGIN:VCARD")
    card.append("VERSION:3.0")
    card.append("END:VCARD")
    return card


def lines_fill(user_info):
    """
    по списку контактных данных
    возвращает отформатированную, дозаполненную
    карту (списком)
    """
    card_lines = lines_pre_gen()

    last_name = user_info[0]
    first_name = user_info[1]
    phone_number = user_info[2]

    name_line = "N:" + last_name + ";" + first_name + ";;;"
    full_name_line = "FN:" + first_name + " " + last_name
    tel = "TEL;type=CELL;type=VOICE;type=pref:" + phone_number

    card_lines.insert(2, name_line)
    card_lines.insert(3, full_name_line)
    card_lines.insert(4, tel)
    return card_lines  # TODO logs


def vcard_gen(user_info, filename="cards.vcf", new=False):
    """
    по списку контактых данных создает vcard пользователя
    опционально можно указать имя файла
    опционально можно указать, создавать ли новый файл, или дописывать в старый
    """
    card = lines_fill(user_info)
    if new:
        mode = "w"
    else:
        mode = "a"
    f = open(filename, mode)  # TODO обработка ошибок! + имя файла по юзверю
    for line in card:
        f.write(line + "\n")
    f.close()


if __name__ == '__main__':
    print("This library can't be started manually!")
    print("Try to import it in your code! EX: vcard_gen(user_info)")
