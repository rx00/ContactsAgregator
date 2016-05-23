import urllib.request
import urllib.parse
import webbrowser
import binascii
import datetime
import logging
import random
import base64
import json
import hmac
import time

from hashlib import sha1
from urllib.request import quote
from utils.authutils import text_caller

logger = logging.getLogger(__name__)


class TwitterApi:
    def __init__(self):
        self.oauth_consumer_key =\
            "1RiattuMQATlvkzfzC3YvuI3j"
        self.oauth_consumer_secret =\
            "LUtjZlx2Lymut8yxcXb8Je7L1u1jZAH9tP5M5SAYSXPgzJDvQt"
        self.oauth_token = ""
        self.oauth_token_secret = ""
        self.screen_name = ""
        self.user_id = ""

    def auth(self):
        """
        :return: заполняет поля идетнификации пользователя в классе
        """
        # STEP 1: Get Request_Token
        request_token_url = "https://api.twitter.com/oauth/request_token"
        request_params = {
            "oauth_callback": "oob",
            "oauth_consumer_key": quote(self.oauth_consumer_key)
        }
        request_keys = [self.oauth_consumer_secret]
        request_info = TwitterApi._extract_tokens(
            TwitterApi.make_request(
                request_token_url,
                request_params,
                request_keys
            )
        )
        logger.debug("Request Token recived")

        # STEP 2: Get oauth_verifier
        pin_code = TwitterApi._get_pin_code(request_info["oauth_token"])
        logger.debug("Pin-Code recived")

        # STEP 3: Get valid oauth tokens
        access_token_url = "https://api.twitter.com/oauth/access_token"
        access_params = {
            "oauth_token": quote(request_info["oauth_token"]),
            "oauth_consumer_key": quote(self.oauth_consumer_key),
            "oauth_verifier": pin_code
        }
        access_keys = [
            self.oauth_consumer_secret,
            request_info["oauth_token_secret"]
        ]
        request_info = TwitterApi._extract_tokens(
            TwitterApi.make_request(
                access_token_url,
                access_params,
                access_keys
            )
        )
        logger.debug("Tokens were written to class fields")

        # STEP 4: Fill Class fields
        self.oauth_token = request_info["oauth_token"]
        self.oauth_token_secret = request_info["oauth_token_secret"]
        self.screen_name = request_info["screen_name"]
        self.user_id = request_info["user_id"]
        logger.debug("Authorization complete for {} with Twitter user_id = "
                     .format(self.screen_name, self.user_id))

    def _get_friends_amount(self):
        """
        :return: количество друзей в твиттере
        """
        request_url = "https://api.twitter.com/1.1/friends/ids.json"
        header = {
            "oauth_token": quote(self.oauth_token),
            "oauth_consumer_key": quote(self.oauth_consumer_key),
        }
        keys = [self.oauth_consumer_secret, self.oauth_token_secret]
        friends_ids = TwitterApi.make_request(
            request_url,
            header,
            keys,
            method="GET"
        )
        friends_ids_dict = json.loads(friends_ids)
        friends_amount = friends_ids_dict["ids"]
        logger.debug("Found {} friends in {} Twitter"
                     .format(friends_amount, self.screen_name))
        return friends_amount

    def get_friends(self):
        """
        :return: json-объект друзей в твиттере
        """
        amount = self._get_friends_amount()
        request_url = "https://api.twitter.com/1.1/friends/list.json"
        request_raw_data = {"count": str(amount)}
        querystring = urllib.parse.urlencode(request_raw_data)
        header = {
            "oauth_token": quote(self.oauth_token),
            "oauth_consumer_key": quote(self.oauth_consumer_key)
        }
        keys = [self.oauth_consumer_secret, self.oauth_token_secret]
        header.update(request_raw_data)
        friends_objects = TwitterApi.make_request(
            request_url,
            header,
            keys,
            method="GET",
            get_query=querystring
        )
        logger.debug("Got friend objects in {} Twitter"
                     .format(self.screen_name))
        return json.loads(friends_objects)

    @staticmethod
    def make_request(url, header_info, keys, method="POST", get_query=None):
        """
        :param url: адрес, на который будет послан запрос
        :param header_info: динамически генерируемые данные хэдера
        :param keys: ключи авторизации
        :param method: (опционально) можно указать вид запроса
        :param get_query: (опционально) параметры к основному url
        :return: строка ответа
        """
        # STEP 1: Create Full Params Dictionary
        params = {}
        params.update(header_info)
        params.update(TwitterApi._get_static_param_set())

        # STEP 2: Get HMAC-SHA1 from params dict and append it to params
        signature = TwitterApi._get_signature(method, url, params, keys)
        params["oauth_signature"] = quote(signature, safe="")
        auth_header = TwitterApi._create_header(params)

        # STEP 3: Build Request and append Header (+url)

        if get_query is not None:
            url += "?{}".format(get_query)

        auth_request = urllib.request.Request(url, method=method)
        auth_request.add_header("Authorization", auth_header)

        # STEP 4: Send Request and read result
        answer = urllib.request.urlopen(auth_request)
        cooked_answer = answer.read().decode()
        return cooked_answer

    @staticmethod
    def _get_pin_code(oauth_token):
        """
        :param oauth_token: токен для формирования запроса и открытия страницы
        :return: pin-code используемый как auth_verifier
        """
        url = "https://api.twitter.com/oauth/authorize?oauth_token={}"\
            .format(oauth_token)
        try:
            print("Авторизуйтесь в Твиттере "
                  "и введите в поле ниже код из браузера!")
            print("URL: {}".format(url))
            time.sleep(4)
            webbrowser.open_new_tab(url)
        except webbrowser.Error:
            print("Произошла проблема с инициализацией браузера,\n"
                  "откройте данный url у себя в браузере для получения\n"
                  "pin-кода!\n{}".format(url))
        pin_code = text_caller("Pin-Code")
        return pin_code

    @staticmethod
    def _get_static_param_set():
        """
        :return: кусок хэдера, присутствующий в любом запросе
        """
        params = {
            "oauth_nonce": urllib.request.quote(TwitterApi._get_nonce()),
            "oauth_timestamp": str(TwitterApi._get_timestamp()),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_version": "1.0"
        }
        return params

    @staticmethod
    def _create_header(params):
        """
        :param params словарь параметров
        :return строка вида "OAuth params
        """
        auth_header = "OAuth "
        for param in sorted(params):
            if "oauth" in param:
                auth_header += '{}="{}", '.format(param, params[param])
        auth_header = auth_header[:-2]
        return auth_header

    @staticmethod
    def _extract_tokens(tokens):
        """
        функция разбора ответа API (авторизация)
        :param tokens: строка, вида a=b&c=d
        :return: словарь из этой строки
        """
        pairs = tokens.split("&")
        answer_list = []
        for pair in pairs:
            answer_list.append(pair.split("="))
        token_dict = {}
        token_dict.update(answer_list)
        return token_dict

    @staticmethod
    def _get_signature(method, link, param_dict, keys):
        """
        функция хэширования запроса:
        :param method - вид запроса POST/GET
        :param link - ссылка к api
        :param param_dict - список параметров хэширования
        :param keys - список ключей хэширования
        :return хэш HMAC-SHA1 в base64 представлении
        """

        raw = ""
        for param in sorted(param_dict):
            raw += "{}={}&".format(quote(param), quote(param_dict[param]))
        params = raw[:-1]

        key = keys[0] + "&"
        if len(keys) > 1:
            key += keys[1]

        cooked_string = method.upper() + "&"\
                                       + quote(link, safe="")\
                                       + "&"\
                                       + quote(params, safe="")

        hashed = hmac.new(
            key=key.encode(),
            msg=cooked_string.encode(),
            digestmod=sha1
        )
        result = binascii.b2a_base64(hashed.digest()).decode().rstrip("\n")
        return result

    @staticmethod
    def _get_nonce():
        """
        :return произвольная строка, состояющяя из a-zA-Z0-9[:32]
        """
        period = random.getrandbits(8 * 32)
        fingerprint = base64.b64encode(bytes(str(period), "utf-8")).decode()
        good_fingerprint = fingerprint.replace("=", "")
        return good_fingerprint[:32]

    @staticmethod
    def _get_timestamp():
        """
        :return текущее время в формате timestamp
        """
        current_time = datetime.datetime.now()
        timestamp_time = int(current_time.timestamp())
        return timestamp_time


if __name__ == '__main__':
    print("Use this as a lib! EX: TwitterApi()")
