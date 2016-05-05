import logging
import binascii
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


class Card:
    def __init__(self, user_info):  # card logging?
        self.vk_id = user_info["vk_id"]
        self.domain = user_info["domain"]
        self.photo = user_info["photo_50"]
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

    def _photo_encoder(self):
        try:
            if self.photo[-3:] == "jpg":
                with urlopen(self.photo) as f:
                    string = f.read()
                    self.photo = binascii.b2a_base64(string).decode()
                    logger.debug("Downloaded and encoded image for {}!"
                                 .format(self.vk_id))
        except URLError:
            logger.debug("Can't reach photo file!")
            self.photo = ""

    def __str__(self):
        """
        преобразует карту в ее строковое представление
        """
        card_lines = Card._lines_pre_gen()
        self._photo_encoder()

        last_name = self.last_name
        first_name = self.first_name
        mobile_phone = self.mobile_phone
        photo = self.photo

        name_line = "N:{};{};;;".format(last_name, first_name)
        full_name_line = "FN:{} {}".format(first_name, last_name)
        tel = "TEL;type=CELL;type=VOICE;type=pref:{}".format(mobile_phone)
        photo_line = "PHOTO;ENCODING=b;TYPE=JPEG:{}".format(photo)

        card_lines.insert(2, name_line)
        card_lines.insert(3, full_name_line)
        card_lines.insert(4, tel)
        if photo:
            card_lines.insert(5, photo_line)

        card = ""
        for line in card_lines:
            card += line + "\n"

        return card


if __name__ == '__main__':
    print("This library can't be started manually!")
    print("Try to import it in your code! EX: Card(user_dict)")
