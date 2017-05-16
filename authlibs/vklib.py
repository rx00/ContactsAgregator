import urllib.response
import urllib.request
import re
import logging
import json

from utils.authutils import text_caller

logger = logging.getLogger(__name__)


class VkApi:
    def __init__(self, permissions="groups,status,wall,offline", await_code=False):
        self.client_id = 5333691
        self.permissions = permissions
        self.token = ""
        self.id = ""
        self.vk_login = None
        self.vk_password = None
        self.await_code = await_code
        self.browser = None
        self.state = "Ожидание старта авторизации"

    def get_tokens(self):
        return {
            "token": self.token,
            "id": self.id
        }

    def set_tokens(self, token_dict):
        self.state = "Токены получены"
        self.token = token_dict["token"]
        self.id = token_dict["id"]

    def get_friends(self, fields, lang="en"):
        """
        по данным авторизации запрашивает список друзей пользователя
        выводит объект json с данными друзей
        """
        vk_id = self.id
        token = self.token

        fields = ",".join(fields)

        url = "https://api.vk.com/method/friends.get?user_id=" + \
              vk_id + \
              "&fields=" + \
              fields + \
              "&lang=" + \
              lang + \
              "&version=5.45" + \
              "&access_token=" + token
        response = urllib.request.urlopen(url).read().decode()
        parsed_json = json.loads(response)

        if "error" in parsed_json:
            raise VkApiError(parsed_json["error"])
        else:
            return parsed_json

    def request_builder(self):
        """
        Постройка запроса для авторизации к api по
        - client_id - идентификатор приложения
        - permissions - права доступа
        возвращает url для обращения к авторизации вк
        """
        self.state = "Старт авторизации..."
        vk_api_version = 5.45
        url = "https://oauth.vk.com/oauth/authorize?" + \
            "redirect_uri=http://oauth.vk.com/blank.html" + \
            "&response_type=token" + \
            "&client_id=" + str(self.client_id) + \
            "&scope=" + str(self.permissions) + \
            "&display=mobile" + \
            "&v=" + str(vk_api_version)
        logger.debug("Auth Form generated for app_id"
                     " = {} with permissions = {}"
                     .format(str(self.client_id), str(self.permissions)))
        return url

    def auth_form_parser(self, response):
        """
        парсер страницы авторизации
        возвращает url для прохождения авторизации
        """
        if response == "":
            raise ValueError("Empty line!")
        raw_html_lines = response.split("\n")
        inputs_list = []
        for line in raw_html_lines:
            if "input type" in line and "function" not in line \
                    or "method=" in line:
                inputs_list.append(re.findall(r'\s.*?=".*?"', line, re.DOTALL))
        address = inputs_list[0][1][9:-1]
        arg_list = list()
        for argument in inputs_list[1:-2]:  # TODO fix? magic constants
            arg = argument[1][7:-1]
            value = argument[2][8:-1]
            arg_list.append(arg + "=" + value + "&")

        if not self.vk_login:
            login = text_caller("Login")
        else:
            login = self.vk_login

        if not self.vk_password:
            password = text_caller("Password", private=True)
        else:
            password = self.vk_password

        full_url = address + "?" + ''.join(arg_list) + \
                             "email=" + urllib.request.quote(login) + \
                             "&pass=" + urllib.request.quote(password)
        logger.debug("Formed auth-request: " + full_url[:35] + "[*]")
        return full_url

    def two_step_auth_parser(self, response):
        """
        парсер страницы двухэтапной авторизации по строке
        возвращает url для прохождения авторизации
        """
        if response == "":
            raise VkApiError
        raw_html_lines = response.split("\n")
        address = "https://m.vk.com"
        hash_line = ""
        for line in raw_html_lines:
            position = line.find("/login?act=authcheck_code")
            if position >= 0:
                hash_line = line[position:-13]  # TODO clever position
        if not self.await_code:
            code_text = text_caller("Auth SMS code")
        else:
            code_text = ""

        check_code = urllib.request.quote(code_text)
        full_url = address + hash_line + "&remember=0" + "&code=" + check_code
        logger.debug("Formed double-auth request: " + full_url[:35] + "[*]")
        return full_url

    def post_auth_verifier(self, response):
        """
        парсер страницы подтверждения работы с данным приложением
        возвращает url для "нажатия кнопки подтверждения"
        """
        if response == "":
            raise VkApiError
        raw_html_lines = response.split("\n")
        full_url = ""
        for line in raw_html_lines:
            position = line.find("https://login.vk.com/?act=grant_access")
            if position >= 0:
                full_url = line[position:-2]
        logger.debug("Formed button-answer request: " + full_url[:35] + "[*]")
        return full_url

    def response_role(self, response):
        """
        по url запроса/содержимому страницы фунция определяет
        тип необходимого обработчика страницы и вызывает его
        возвращает кортеж вида (идентификатор_содержимого, [url])
        """
        response_url = response.geturl()
        if "://oauth.vk.com/blank.html#access_token=" in response_url:
            logger.debug("Found Token")
            return 1, response_url
        else:
            # print(response_url)  # hard debug line
            response_page = response.read().decode()
            if "неверный логин или пароль" in response_page:
                logger.debug("Bad Login")
                return 4,  # bad login

            elif "<b>код подтверждения</b> из SMS" in response_page:
                logging.debug("SMS auth started")
                answer_url = self.two_step_auth_parser(response_page)
                if self.await_code:
                    return -1, answer_url
                return 3, answer_url

            elif "Для продолжения Вам необходимо войти" in response_page:
                logger.debug("Login form opened")
                answer_url = self.auth_form_parser(response_page)
                return 2, answer_url  # some trouble?0_o

            elif "Приложению будут доступны:" in response_page:
                logger.debug("Access button form opened")
                answer_url = self.post_auth_verifier(response_page)
                return 5, answer_url  # first auth in current app

            elif "в личном сообщении от Администрации" in response_page:
                logging.debug("Need for private message, redirecting to SMS")
                answer_url = self.two_step_auth_parser(response_page)
                if self.await_code:
                    return -1, answer_url
                return 3, answer_url
            else:
                return 6,  # something_bad

    def token_parser(self, token_url):
        """
        Функция возвращает кортеж по url токена
        В кортеже содержится id и token пользователя
        (id, token)
        """
        token_start_key = "access_token="
        token_start = token_url.find(token_start_key)
        token_end_key = "&expires_in"
        token_end = token_url.find(token_end_key)
        token = token_url[token_start+len(token_start_key):token_end]
        user_id_start_key = "user_id="
        user_id_start = token_url.find(user_id_start_key)
        user_id = token_url[user_id_start+len(user_id_start_key):]
        logger.debug("Parsed user id = " + user_id +
                     " with token = " + token[:5] +
                     "*")
        return {"user_id": user_id, "token": token}

    def auth(self, custom_url=""):
        """
        Обновит поля id и token класса при успешном парсинге
        """
        if not custom_url:
            self.browser = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor,
                urllib.request.HTTPRedirectHandler
            )

            logger.debug("=== VK Auth Session ===")

            first_response = self.browser.open(
                self.request_builder()
            )
            auth_answer = self.auth_form_parser(first_response.read().decode())
            join_response = self.browser.open(auth_answer)
            page_role = self.response_role(join_response)
        else:
            page_role = 3, custom_url
        while True:
            if page_role[0] == 1:
                self.state = "Токены получены"
                tokens = self.token_parser(page_role[1])
                self.token = tokens["token"]
                self.id = tokens["user_id"]
                break
            elif page_role[0] == 4:
                self.state = "Неверный логин или пароль"
                logging.debug("Bad login")
                raise VkApiError("Указан неверный логин или пароль!")
            elif page_role[0] == 6:
                self.state = "Неизвестная ошибка"
                logging.debug("Unknown error")
                print("Неизвестная ошибка!")
                raise VkApiError(page_role)
            elif page_role[0] == -1:
                logging.debug("Stopped loop due to awaiting two step code!")
                self.state = "Ожидание кода двухэтапной авторизации..."
                self.await_code = page_role[1]
                break
            else:
                url_from_page = page_role[1]
                response = self.browser.open(url_from_page)
                page_role = self.response_role(response)


class VkApiError(Exception):
    pass

if __name__ == '__main__':
    print("This library can't be started manually!")
    print("Try to import it in your code! EX: auth(client_id, permissions)")
