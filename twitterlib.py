import urllib.response
import urllib.request
import tweepy


def twitter_auth_formatter(response):

    pass


def twitter_auth():
    consumer_key = "1RiattuMQATlvkzfzC3YvuI3j"
    consumer_secret = "LUtjZlx2Lymut8yxcXb8Je7L1u1jZAH9tP5M5SAYSXPgzJDvQt"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url()
    print(auth_url)
    auth.get_username()
    browser = urllib.request.build_opener(
        urllib.request.HTTPRedirectHandler,
        urllib.request.HTTPCookieProcessor
    )
    answer = browser.open(auth_url).read().decode()
    parsed_answer = answer.split("\n")
    #goods_in = answe
    pass



#twitter_auth()
