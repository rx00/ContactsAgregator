import urllib.request
import urllib.parse
import webbrowser
import binascii
import datetime
import random
import base64
import hmac
import time

from hashlib import sha1
from urllib.request import quote

#refact
import ssl


def twitter_auth():
    consumer_key = "1RiattuMQATlvkzfzC3YvuI3j"
    consumer_secret = "LUtjZlx2Lymut8yxcXb8Je7L1u1jZAH9tP5M5SAYSXPgzJDvQt"
    request_info = get_request_token(consumer_key, consumer_secret)
    pin_code = get_pin_code(request_info["oauth_token"])

    request_info = get_verifier(
        consumer_key,
        consumer_secret,
        request_info["oauth_token"],
        request_info["oauth_token_secret"],
        pin_code
    )

    print(request_info)


def get_verifier(consumer_key, consumer_secret, oauth_token, oauth_secret, pin_code):
    method = "POST"
    url = "https://api.twitter.com/oauth/access_token"
    params = {
        "oauth_token": quote(oauth_token),
        "oauth_consumer_key": quote(consumer_key),
        "oauth_verifier": pin_code
    }
    params.update(get_static_param_set())
    signature = get_signature(method, url, params, [consumer_secret, oauth_secret])
    params["signature"] = quote(signature, safe="")
    auth_header = create_header(params)

    #debug
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    #debug

    auth_request = urllib.request.Request(url, method="POST")
    auth_request.add_header("Authorization", auth_header)

    answer = urllib.request.urlopen(auth_request, context=ctx)
    tokens = answer.read().decode()
    return extract_tokens(tokens)


def get_pin_code(oauth_token):
    url = "https://api.twitter.com/oauth/authorize?oauth_token={}"\
        .format(oauth_token)
    try:
        print("Авторизуйтесь в Твиттере и введите сюда код из браузера!")
        time.sleep(5)
        webbrowser.open_new_tab(url)
    except webbrowser.Error:
        print("Произошла проблема с инициализацией браузера,\n"
              "откройте данный url у себя в браузере для получения\n"
              "pin-кода!\n{}".format(url))
    pin_code = input("Pin-Code: ")  # TODO подключить утилиты
    return pin_code


def get_static_param_set():
    """
    :return: кусок хэдера, присутствующий в любом запросе
    """
    params = {
        "oauth_nonce": urllib.request.quote(get_nonce()),
        "oauth_timestamp": str(get_timestamp()),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_version": "1.0"
    }
    return params


def get_request_token(consumer_key, consumer_secret):
    """
    :param consumer_key: ключ приложения
    :param consumer_secret: ключ шифрования приложением
    :return:
    """
    method = "POST"
    url = "https://api.twitter.com/oauth/request_token"
    params = {
        "oauth_callback": "oob",
        "oauth_consumer_key": quote(consumer_key)
    }
    params.update(get_static_param_set())
    signature = get_signature(method, url, params, [consumer_secret])
    params["oauth_signature"] = quote(signature, safe="")

    auth_header = create_header(params)

    #debug
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    #debug

    auth_request = urllib.request.Request(url, method="POST")
    auth_request.add_header("Authorization", auth_header)

    answer = urllib.request.urlopen(auth_request, context=ctx)
    tokens = answer.read().decode()
    token_dict = extract_tokens(tokens)
    return token_dict


def create_header(params):
    """
    :param params словарь параметров
    :return строка вида "OAuth {}", где {} - лексиграфически отсортированные параметры
    """
    auth_header = "OAuth "
    for param in sorted(params):
        auth_header += '{}="{}", '.format(param, params[param])
    auth_header = auth_header[:-2]
    return auth_header


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


def get_nonce():
    """
    :return произвольная строка, состояющяя из a-zA-Z0-9, длинна 32 символа
    """
    period = random.getrandbits(8 * 32)
    fingerprint = base64.b64encode(bytes(str(period), "utf-8")).decode()
    good_fingerprint = fingerprint.replace("=", "")
    return good_fingerprint[:32]


def get_timestamp():
    """
    :return текущее время в формате timestamp
    """
    current_time = datetime.datetime.now()
    timestamp_time = int(current_time.timestamp())
    return timestamp_time


if __name__ == '__main__':
    twitter_auth()
