class Card:
    def __init__(self, user_info):
        self.last_name = user_info["last_name"]
        self.first_name = user_info["first_name"]
        self.mobile_phone = user_info["mobile_phone"]

    @staticmethod
    def _lines_pre_gen():
        """
        Возвращает заготовку карты (списком)
        для строкового представления карты
        """
        card = list()
        card.append("BEGIN:VCARD")
        card.append("VERSION:3.0")
        card.append("END:VCARD")
        return card

    def __str__(self):
        """
        преобразует карту в ее строковое представление
        """
        card_lines = Card._lines_pre_gen()

        last_name = self.last_name
        first_name = self.first_name
        mobile_phone = self.mobile_phone

        name_line = "N:{};{};;;".format(last_name, first_name)
        full_name_line = "FN:{} {}".format(first_name, last_name)
        tel = "TEL;type=CELL;type=VOICE;type=pref:{}".format(mobile_phone)

        card_lines.insert(2, name_line)
        card_lines.insert(3, full_name_line)
        card_lines.insert(4, tel)

        card = ""
        for line in card_lines:
            card += line + "\n"

        return card  # TODO logs


if __name__ == '__main__':
    print("This library can't be started manually!")
    print("Try to import it in your code! EX: Card(user_dict)")
