import urllib.response
import urllib.request
import re
import tweepy
import webbrowser
from utils.authutils import text_caller

def twitter_auth_formatter(response):
    pass


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

    print(auth.access_token)
    print(auth.access_token_secret)


def first_auth(answer):
    parsed_answer = answer.split("\n")

    lines = []
    for line in parsed_answer:
        if "<form" in line or "input" in line:
            lines.append((re.findall(r'\s.*?=".*?"', line, re.DOTALL)))

    arg_list = []
    action_id = 'action="'
    name_id = 'name="'
    value_id = 'value="'
    form_position = lines[0][0].find(action_id)
    arg_list.append(lines[0][0][form_position + len(action_id):-1])
    for line in lines[1:]:
        for arg in line:
            name_position = arg.find(name_id)
            value_position = arg.find(value_id)
            if name_position >= 0:
                arg_list.append(arg[name_position + len(name_id):-1])
            if value_position >= 0:
                arg_list.append(arg[value_position + len(value_id):-1])
    login = text_caller("Login")
    password = text_caller("Password", private=True)
    arg_list[10] = password
    arg_list[8] = login
    url = arg_list[0] + "?"
    form_result = ""
    iteration = 1
    # print(arg_list)
    for arg in arg_list[1:-3]:
        symbol = "&" if iteration % 2 == 0 else "="
        form_result += arg + symbol
        iteration += 1
    print(url+form_result[:-1])
    return url + form_result[:-1]


twitter_auth()
