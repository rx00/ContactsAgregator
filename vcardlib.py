import logging
import binascii
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)


class Card:
    def __init__(self, user_info):
        self.vk_id = user_info["vk_id"]
        self.vk_domain = user_info["domain"]
        self.twitter_domain = ""
        self.photo = user_info["photo_50"]
        self.last_name_en = user_info["last_name"]  # merge factor
        self.first_name_en = user_info["first_name"]  # merge factor
        self.mobile_phone = user_info["mobile_phone"]
        self.image = ""

    @staticmethod
    def _lines_pre_gen():
        """
        Возвращает заготовку карты (списком)
        для строкового представления карты
        """
        card = list()
        card.append("BEGIN:VCARD")
        card.append("VERSION:3.0")
        card.append("item1.X-ABLabel:Вконтакте")
        card.append("item2.X-ABLabel:Твиттер")
        card.append("END:VCARD")
        return card

    def _photo_encoder(self):
        """
        качаем фото по ссылки из поля photo и пишем
        base64 строку в image
        """
        try:
            if self.photo[-3:] == "jpg":  # jpg у юзеров, png - системное
                with urlopen(self.photo) as f:
                    string = f.read()
                    self.image = binascii.b2a_base64(string).decode()
                    logger.debug("Downloaded and encoded image for {}!"
                                 .format(self.vk_id))
        except URLError:
            logger.debug("Can't reach photo file!")
            self.image = ""

    def __str__(self):
        """
        преобразует карту в ее строковое представление
        """
        card_lines = Card._lines_pre_gen()
        self._photo_encoder()

        name_line = "N:{};{};;;"\
            .format(self.last_name_en, self.first_name_en)
        full_name_line = "FN:{} {}"\
            .format(self.first_name_en, self.last_name_en)
        tel = "TEL;type=CELL;type=VOICE;type=pref:{}"\
            .format(self.mobile_phone)
        photo_line = "PHOTO;ENCODING=b;TYPE=JPEG:{}"\
            .format(self.image)
        vk_social_link = "item1.URL;type=pref:vk.com/{}"\
            .format(self.vk_domain)
        tw_social_link = "item2.URL;type=pref:twitter.com/{}"\
            .format(self.twitter_domain)

        card_lines.insert(2, name_line)
        card_lines.insert(3, full_name_line)
        card_lines.insert(4, tel)
        card_lines.insert(5, vk_social_link)
        if self.image:
            card_lines.insert(6, photo_line)
        if self.twitter_domain:
            card_lines.insert(7, tw_social_link)

        card = ""
        for line in card_lines:
            card += line + "\n"

        return card


if __name__ == '__main__':
    print("This library can't be started manually!")
    print("Try to import it in your code! EX: Card(user_dict)")
