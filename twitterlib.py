import urllib.response
import urllib.request
import re
import tweepy
from utils.authutils import text_caller

def twitter_auth_formatter(response):
    pass


def twitter_auth():
    consumer_key = "1RiattuMQATlvkzfzC3YvuI3j"
    consumer_secret = "LUtjZlx2Lymut8yxcXb8Je7L1u1jZAH9tP5M5SAYSXPgzJDvQt"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url()
    print(auth_url)
    # auth.get_username()
    browser = urllib.request.build_opener(
        urllib.request.HTTPRedirectHandler,
        urllib.request.HTTPCookieProcessor
    )
    answer = browser.open(auth_url).read().decode()
    parsed_answer = answer.split("\n")
    lines = []
    for line in parsed_answer:
        if "<form" in line or "input" in line:
            lines.append((re.findall(r'\s.*?=".*?"', line, re.DOTALL)))
    #print(lines)
    arg_list = []
    action_id = 'action="'
    name_id = 'name="'
    value_id = 'value="'
    form_position = lines[0][0].find(action_id)
    arg_list.append(lines[0][0][form_position+len(action_id):-1])
    for line in lines[1:]:
        for arg in line:
            name_position = arg.find(name_id)
            value_position = arg.find(value_id)
            if name_position >= 0:
                arg_list.append(arg[name_position+len(name_id):-1])
            if value_position >= 0:
                arg_list.append(arg[value_position+len(value_id):-1])

    login = text_caller("Login")
    password = text_caller("Password", private=True)

    arg_list[10] = password
    arg_list[8] = login

    form_result = arg_list[0] + "?"
    iteration = 1
    for arg in arg_list[1:-5]:
        symbol = "&" if iteration % 2 == 0 else "="
        form_result += arg + symbol
        iteration += 1
    print(form_result[:-1])


twitter_auth()
