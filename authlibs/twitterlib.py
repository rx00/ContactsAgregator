import tweepy
import json
import webbrowser
from utils.authutils import text_caller


def twitter_auth():
    consumer_key = "1RiattuMQATlvkzfzC3YvuI3j"
    consumer_secret = "LUtjZlx2Lymut8yxcXb8Je7L1u1jZAH9tP5M5SAYSXPgzJDvQt"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    twitter_auth_url = auth.get_authorization_url()

    try:
        webbrowser.open_new_tab(twitter_auth_url)
    except webbrowser.Error:
        print("Не удалось открыть системный веб-браузер!\n" +
              "Перейдите по данному url в Вашем веб-браузере, для получения PIN-кода!\n{}"
              .format(twitter_auth_url)
              )

    print("Введите полученный в процессе авторизации PIN-код")
    pin_code = text_caller("PIN")

    auth.get_access_token(pin_code)

    return consumer_key, consumer_secret,\
        auth.access_token, auth.access_token_secret


def friend_parser(keys):
    auth = tweepy.OAuthHandler(keys[0], keys[1])
    auth.access_token = keys[2]
    auth.access_token_secret = keys[3]

    api = tweepy.API(auth)
    b = api.friends()

    for obj in b:
        new = json.loads(obj)
        print(new)
        print(new[0])
        print()


def starter():
    friend_parser(twitter_auth())


if __name__ == '__main__':
    print("I'am lib!")
