import urllib.request
import urllib.parse
import webbrowser
import binascii
import datetime
import random
import base64
import json
import hmac
import time

from hashlib import sha1
from urllib.request import quote


class TwitterApi:
    def __init__(self):
        self.consumer_key = "1RiattuMQATlvkzfzC3YvuI3j"
        self.consumer_secret = "LUtjZlx2Lymut8yxcXb8Je7L1u1jZAH9tP5M5SAYSXPgzJDvQt"
        self.oauth_token = ""
        self.oauth_token_secret = ""
        self.screen_name = ""
        self.user_id = ""

    def auth(self):
        # STEP 1: Get Request_Token
        request_token_url = "https://api.twitter.com/oauth/request_token"
        request_params = {
            "oauth_callback": "oob",
            "oauth_consumer_key": quote(self.consumer_key)
        }
        request_keys = [self.consumer_secret]
        request_info = TwitterApi.extract_tokens(
            TwitterApi.make_request(request_token_url, request_params, request_keys)
        )

        # STEP 2: Get oauth_verifier
        pin_code = TwitterApi.get_pin_code(request_info["oauth_token"])

        # STEP 3: Get valid oauth tokens
        access_token_url = "https://api.twitter.com/oauth/access_token"
        access_params = {
            "oauth_token": quote(request_info["oauth_token"]),
            "oauth_consumer_key": quote(self.consumer_key),
            "oauth_verifier": pin_code
        }
        access_keys = [
            self.consumer_secret,
            request_info["oauth_token_secret"]
        ]
        request_info = TwitterApi.extract_tokens(
            TwitterApi.make_request(access_token_url, access_params, access_keys)
        )

        # STEP 4: Fill Class fields
        self.oauth_token = request_info["oauth_token"]
        self.oauth_token_secret = request_info["oauth_token_secret"]
        self.screen_name = request_info["screen_name"]
        self.user_id = request_info["user_id"]

    def _get_friends_amount(self):
        request_url = "https://api.twitter.com/1.1/friends/ids.json"
        header = {
            "oauth_token": quote(self.oauth_token),
            "oauth_consumer_key": quote(self.consumer_key),
        }
        keys = [self.consumer_secret, self.oauth_token_secret]
        friends_ids = TwitterApi.make_request(
            request_url,
            header,
            keys,
            method="GET"
        )
        friends_ids_dict = json.loads(friends_ids)
        return len(friends_ids_dict["ids"])

    def get_friends(self):
        amount = self._get_friends_amount()
        request_url = "https://api.twitter.com/1.1/friends/list.json"
        data = "count={}".format(str(amount))
        # TODO # make byte data + fill header with "count": "20/50/100"

    @staticmethod
    def make_request(url, header_info, keys, method="POST", data=None):

        # STEP 1: Create Full Params Dictionary
        params = {}
        params.update(header_info)
        params.update(TwitterApi.get_static_param_set())

        # STEP 2: Get HMAC-SHA1 from params dict and append it to params
        signature = TwitterApi.get_signature(method, url, params, keys)
        params["oauth_signature"] = quote(signature, safe="")
        auth_header = TwitterApi.create_header(params)

        # STEP 3: Build Request and append Header
        auth_request = urllib.request.Request(url, method=method, data=data)
        auth_request.add_header("Authorization", auth_header)

        # STEP 4: Send Request and read result
        answer = urllib.request.urlopen(auth_request)
        cooked_answer = answer.read().decode()
        return cooked_answer

    @staticmethod
    def get_pin_code(oauth_token):
        url = "https://api.twitter.com/oauth/authorize?oauth_token={}"\
            .format(oauth_token)
        try:
            print("Авторизуйтесь в Твиттере и введите в поле ниже код из браузера!")
            time.sleep(5)
            webbrowser.open_new_tab(url)
        except webbrowser.Error:
            print("Произошла проблема с инициализацией браузера,\n"
                  "откройте данный url у себя в браузере для получения\n"
                  "pin-кода!\n{}".format(url))
        pin_code = input("Pin-Code: ")  # TODO подключить утилиты
        return pin_code

    @staticmethod
    def get_static_param_set():
        """
        :return: кусок хэдера, присутствующий в любом запросе
        """
        params = {
            "oauth_nonce": urllib.request.quote(TwitterApi.get_nonce()),
            "oauth_timestamp": str(TwitterApi.get_timestamp()),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_version": "1.0"
        }
        return params

    @staticmethod
    def create_header(params):
        """
        :param params словарь параметров
        :return строка вида "OAuth {}", где {} - лексиграфически отсортированные параметры
        """
        auth_header = "OAuth "
        for param in sorted(params):
            if "oauth" in param:
                auth_header += '{}="{}", '.format(param, params[param])
        auth_header = auth_header[:-2]
        return auth_header

    @staticmethod
    def extract_tokens(tokens):
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
    def get_signature(method, link, param_dict, keys):
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
    def get_nonce():
        """
        :return произвольная строка, состояющяя из a-zA-Z0-9, длинна 32 символа
        """
        period = random.getrandbits(8 * 32)
        fingerprint = base64.b64encode(bytes(str(period), "utf-8")).decode()
        good_fingerprint = fingerprint.replace("=", "")
        return good_fingerprint[:32]

    @staticmethod
    def get_timestamp():
        """
        :return текущее время в формате timestamp
        """
        current_time = datetime.datetime.now()
        timestamp_time = int(current_time.timestamp())
        return timestamp_time


if __name__ == '__main__':
    user_ex = TwitterApi()
    user_ex.auth()
    user_ex.get_friends()
