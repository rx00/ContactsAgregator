import sys
import os
import logging

from importlib.util import find_spec

import utils.vk_parser
from utils.twitter_parser import user_extractor

from utils.authutils import text_caller
from authlibs.vklib import VkApi
from authlibs.twitterlib import TwitterApi
from vcardlib import Card


if find_spec("Crypto") is not None:
    import authdata


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


class Main:
    def __init__(self, card_file, data_file, data_support):
        self.card_file = card_file
        self.data_file = data_file
        self.data_support = data_support
        self.card_list = []
        self.master_key = None

    def create_cards(self, contacts):
        for contact in contacts:
            self.card_list.append(Card(contact))

    def export_contacts(self):
        if len(self.card_list) > 0:
            try:
                with open(self.card_file, "w") as card_storage:
                    i = 1
                    for card in self.card_list:
                        card_storage.write(str(card))
                        domain_str = ""
                        if card.twitter_domain:
                            domain_str += " + (Twitter)"
                        print("[{}/{}] Контакт {} {} создан (ВКонтакте){}".format(
                            i,
                            len(self.card_list),
                            card.last_name_en,
                            card.first_name_en,
                            domain_str
                        ))
                        i += 1
            except OSError:
                print("Программа не может получить доступ к файлу {}!"
                      .format(self.card_file))
        else:
            print("Ваши друзья не хотят делиться мобильными телефонами ;(")

    def run_vk_auth(self):
        """
        главный авторизатор ВКонтакте
        """
        auth_resources = {
            "permissions": "friends,offline",
            "client_id": 5333691
        }

        bad_token = True
        bad_key = False

        if self.data_support:
            logging.debug("Crypto library found!")
            if not os.path.isfile(self.data_file):
                print("Для начала работы с программой, "
                      "придумайте свой пароль,\n"
                      "ваши данные для авторизации!")
                self.master_key = text_caller("Master-key")
            else:
                self.master_key = text_caller("Master-key")
                vk_data = authdata.get_tokens(
                    "vk",
                    self.master_key,
                    self.data_file
                )
                if "token" in vk_data:
                    print("Введен верный мастер-ключ!")
                    auth_resources["token"] = vk_data["token"]
                    auth_resources["id"] = vk_data["id"]
                    bad_token = False
                    logging.debug("Old data mined, vk session still alive!")
                else:
                    bad_key = True
                    print("Введен неверный мастер-ключ!")
        else:
            logging.debug("Crypto library not found, turning off data module!")
            print("Библиотека Crypto не найдена!\n"
                  "Сохранение данных авторизации не поддерживается!")

        auth_info = VkApi(auth_resources)
        vk_user_info = {
            "token": auth_info.token,
            "id": auth_info.id
        }

        if self.data_support:
            if bad_token:
                if bad_key:
                    print(
                        "Создайте новый мастер-ключ: "
                        "(ВНИМАНИЕ! Старые данные удалятся!)"
                          )
                    self.master_key = text_caller("Master-key")
                authdata.write_tokens(
                    "vk",
                    self.master_key,
                    vk_user_info,
                    self.data_file
                )

        if auth_info.token == "":
            print("Авторизация не удалась")
            raise AuthError

        return auth_info

    def run_twitter_auth(self):
        twitter_user = TwitterApi()
        if self.data_support:
            data = authdata.get_tokens(
                "tw",
                self.master_key,
                self.data_file
            )
            if "oauth_token" in data:
                twitter_user.load_auth_dict(data)
            else:
                twitter_user.auth()
                authdata.write_tokens(
                    "tw",
                    self.master_key,
                    twitter_user.get_auth_dict(),
                    self.data_file
                )
        else:
            twitter_user.auth()
        return twitter_user

    def contacts_aggregator(self):
        print("===> Экспорт адресной книги <===")
        logging.debug("===> Application started <===")

        fields = ("domain", "contacts", "photo_50")

        auth_data = self.run_vk_auth()
        parsed_json = auth_data.get_friends(fields)

        print("Вы успешно авторизовались в социальной сети ВКонтакте!")
        raw_users = utils.vk_parser.filter_by_mobile(parsed_json)
        vk_contacts = utils.vk_parser.extract_correct_mobiles(raw_users)
        print("Найдено {} контактов c мобильными телефонами у {} друзей!"
              .format(len(vk_contacts), len(raw_users)))

        self.create_cards(vk_contacts)

        print("Список контактов выгружен из ВКонтакте")

        print("Хотите загрузить дополнительную информацию"
              " о друзьях из твиттера?")
        run_twitter = input("Выгрузить твиттер? [Y/n]")
        if run_twitter == "" or run_twitter == "Y":
            print("Начинаю дополнительную загрузку контактов из твиттера!")
            twitter_user = self.run_twitter_auth()
            self.run_merger(twitter_user)

        self.export_contacts()

    def run_merger(self, twitter_user):
        twitter_friends_json = twitter_user.get_friends()
        twitter_vk_ids = user_extractor(twitter_friends_json)
        occurences = 0
        for friend_id in twitter_vk_ids.keys():
            for card in self.card_list:
                twitter_vk = twitter_vk_ids[friend_id]["current_mined_vk"]
                if card.vk_domain == twitter_vk:
                    card.twitter_domain = \
                        twitter_vk_ids[friend_id]["current_domain"]
                    logging.debug("Merged vk:{} with tw:{}".format(
                        card.vk_domain,
                        card.twitter_domain
                    ))
                    occurences += 1
        print("Найдено {} совпадений контактов Twitter с Вконтакте"
              .format(occurences))


class AuthError(Exception):
    pass


def main():
    """
    точка входа в приложение
    """
    debug = False
    cards = "cards.vcf"
    data = "data"
    data_support = find_spec("Crypto") is not None

    if len(sys.argv) > 1:
        if "--help" in sys.argv:
            print("====> Генератор адресной книги <====\n"
                  "В данный момент, программа нуждается в\n"
                  "дополнительных аргументах(--debug).\n"
                  "Запуск: python3 {}\n"
                  "Программе требуются права на запись в папку"
                  .format(sys.argv[0]))
            sys.exit()
        elif "--debug" in sys.argv:
            debug = True
            print("Программа запущена в режиме дебага!")
    init_logger(debug)
    try:
        main_point = Main(cards, data, data_support)
        main_point.contacts_aggregator()
    except AuthError:
        print("Не удалось авторизоваться!")
    except SystemExit:
        print("Программа успешно остановлена!")


if __name__ == '__main__':
    main()
