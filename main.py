import sys
import os
import logging
import argparse

from importlib.util import find_spec

import utils.vk_parser
from utils.twitter_parser import user_extractor

from utils.authutils import text_caller
from authlibs.vklib import VkApi
from authlibs.vklib import VkApiError
from authlibs.vk_auth_patch import authorize
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
        self.web_auth = False

    def create_cards(self, contacts):
        """
        :param contacts: список контактов
        :return: инициализирует поле класса списком контактов
        """
        for contact in contacts:
            self.card_list.append(Card(contact))

    def export_contacts(self):
        """
        :return: экспортирует контакты в файл,
         предопределенный полем card_file (vCard формат)
        """
        if self.card_list:
            try:
                with open(self.card_file, "w") as card_storage:
                    i = 1
                    for card in self.card_list:
                        try:
                            card_storage.write(str(card))
                        except KeyboardInterrupt:
                            print("Вы прервали процесс записи контактов!\n"
                                  "Файл может быть поврежден!")
                            sys.exit()
                        domain_str = ""
                        if card.twitter_domain:
                            domain_str += " + (Twitter)"
                        print("[{}/{}] Контакт {} {} создан (ВКонтакте){}"
                              .format(
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

    def get_master_key(self):
        if self.data_support:
            logging.debug("Crypto library found!")
            if not os.path.isfile(self.data_file):
                print("Для начала работы с программой, "
                      "придумайте свой пароль,\n"
                      "ваши данные для авторизации!")
                self.master_key = text_caller("Master-key")
            else:
                self.master_key = text_caller("Master-key")
                data = authdata.get_tokens("vk",
                                           self.master_key, self.data_file)
                if len(data) == 0:
                    raise AuthError()

    def run_vk_auth(self):
        vk_user = VkApi()

        if self.data_support:
            data = authdata.get_tokens(
                "vk",
                self.master_key,
                self.data_file
            )
            if "token" in data:
                vk_user.set_tokens(data)
                return vk_user

        try:
            if self.web_auth:
                data = authorize(5333691)
                vk_user.set_tokens(data)
                if self.data_support:
                    authdata.write_tokens(
                        "vk",
                        self.master_key,
                        vk_user.get_tokens(),
                        self.data_file
                    )
                return vk_user
        except Exception:
            pass

        vk_user.auth()
        if self.data_support:
            authdata.write_tokens(
                "vk",
                self.master_key,
                vk_user.get_tokens(),
                self.data_file
            )
        return vk_user

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

        try:
            self.get_master_key()
        except AuthError:
            print("Вы ввели неверный мастер-ключ!\n"
                  "Удалите файл с данными авторизации, чтобы пересоздать мастер-ключ!")
            sys.exit()

        try:
            auth_data = self.run_vk_auth()
        except VkApiError:
            print("Ошибка авторизации ВКонтакте! Завершение программы.")
            sys.exit()

        vk_fields = ("domain", "contacts", "photo_50")
        parsed_json = auth_data.get_friends(vk_fields)

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

    def run_merger(self, twitter_user):  # TODO clever merger
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


def parse_args():
    description = "Contacts Aggregator:\n" \
                  "Collects and exports your " \
                  "friend's information from " \
                  "social networks"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-c", "--cardfile",
                        action="store",
                        help="cards storage",
                        default="cards.vcf")
    parser.add_argument("--debug",
                        action="store_const",
                        help="debug mode",
                        const="True")
    parser.add_argument("-d", "--data",
                        action="store",
                        help="authorization storage",
                        default="data")
    parser.add_argument("--nocrypto",
                        action="store_const",
                        help="disable auth storage module",
                        const="True"
                        )
    parser.add_argument("--webauth",
                        action="store_const",
                        help="run web auth",
                        const="True")
    return parser.parse_args()


def main():
    """
    точка входа в приложение
    """
    args = parse_args()

    debug = args.debug is not None
    webauth = args.webauth is not None
    cards = args.cardfile
    data = args.data

    data_support = find_spec("Crypto") is not None

    if args.nocrypto is not None:
        data_support = False

    init_logger(debug)
    try:
        main_point = Main(cards, data, data_support)
        if webauth:
            main_point.web_auth = True
        main_point.contacts_aggregator()
    except AuthError:
        print("Не удалось авторизоваться!")
    except SystemExit:
        print("Программа успешно остановлена!")


class AuthError(Exception):
    pass


if __name__ == '__main__':
    main()
