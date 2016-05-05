import urllib.response
import urllib.request
import re
import logging

from utils.authutils import text_caller

logger = logging.getLogger(__name__)


class VkApi:
    def __init__(self, user_data):
        if "token" in user_data:
            self.token = user_data["token"]
            self.id = user_data["id"]
        else:
            client_id = user_data["client_id"]
            permissions = user_data["permissions"]
            auth_results = VkApi.auth(client_id, permissions)
            if len(auth_results) > 0:
                self.token = auth_results["token"]
                self.id = auth_results["user_id"]
            else:
                self.token = ""
                self.id = ""

    @staticmethod
    def request_builder(client_id, permissoins):
        """
        Постройка запроса для авторизации к api по
        - client_id - идентификатор приложения
        - permissions - права доступа
        возвращает url для обращения к авторизации вк
        """
        vk_api_version = 5.45
        url = "https://oauth.vk.com/oauth/authorize?" + \
            "redirect_uri=http://oauth.vk.com/blank.html" + \
            "&response_type=token" + \
            "&client_id=" + str(client_id) + \
            "&scope=" + str(permissoins) + \
            "&display=mobile" + \
            "&v=" + str(vk_api_version)
        logger.debug("Auth Form generated for app_id = " + str(client_id) +
                     " with permissions = " + str(permissoins))
        return url

    @staticmethod
    def auth_form_parser(response):
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

        login = text_caller("Login")
        password = text_caller("Password", private=True)

        full_url = address + "?" + ''.join(arg_list) + \
                             "email=" + urllib.request.quote(login) + \
                             "&pass=" + urllib.request.quote(password)  # UTF8 fix
        logger.debug("Formed auth-request: " + full_url[:35] + "[*]")  # logs
        return full_url

    @staticmethod
    def two_step_auth_parser(response):
        """
        парсер страницы двухэтапной авторизации по строке
        возвращает url для прохождения авторизации
        """
        if response == "":
            raise ValueError("Empty line!")
        raw_html_lines = response.split("\n")
        address = "https://m.vk.com"
        hash_line = ""
        for line in raw_html_lines:
            position = line.find("/login?act=authcheck_code")
            if position >= 0:
                hash_line = line[position:-13]  # TODO сделать авто-поиск позиции
        check_code = urllib.request.quote(text_caller("Auth SMS code"))
        full_url = address + hash_line + "&code=" + check_code + "&remember=0"
        logger.debug("Formed double-auth request: " + full_url[:35] + "[*]")
        return full_url

    @staticmethod
    def post_auth_verifier(response):
        """
        парсер страницы подтверждения работы с данным приложением
        возвращает url для "нажатия кнопки подтверждения"
        """
        if response == "":
            raise ValueError("Empty line!")
        raw_html_lines = response.split("\n")
        full_url = ""
        for line in raw_html_lines:
            position = line.find("https://login.vk.com/?act=grant_access")
            if position >= 0:
                full_url = line[position:-2]
        logger.debug("Formed button-answer request: " + full_url[:35] + "[*]")
        return full_url

    @staticmethod
    def response_role(response):
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
                answer_url = VkApi.two_step_auth_parser(response_page)
                return 3, answer_url  # sms auth

            elif "Для продолжения Вам необходимо войти" in response_page:
                logger.debug("Login form opened")
                answer_url = VkApi.auth_form_parser(response_page)
                return 2, answer_url  # some trouble?0_o

            elif "Приложению будут доступны:" in response_page:
                logger.debug("Access button form opened")
                answer_url = VkApi.post_auth_verifier(response_page)
                return 5, answer_url  # first auth in current app

            else:
                return 6,  # something_bad

    @staticmethod
    def token_parser(token_url):
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

    @staticmethod
    def auth(client_id, permissions):  # TODO фикс дебага!, сделать адекватно!
        """
        Фукция возвращает данные авторизации по правам и идентификатору приложения
        Опционально, функция может писать в дебаг файл (debug=True)
        Опционально, можно указать имя дебаг-файла (debug_file=filename.log)
        Вернет пустой кортеж в случае ошибки
        Вернет кортеж и id и token пользователя при успешном парсинге
        """
        browser = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor,
            urllib.request.HTTPRedirectHandler
        )

        logger.debug("=== Auth Session ===")

        first_response = browser.open(VkApi.request_builder(client_id, permissions))
        auth_answer = VkApi.auth_form_parser(first_response.read().decode())
        join_response = browser.open(auth_answer)
        page_role = VkApi.response_role(join_response)
        while True:
            if page_role[0] == 1:
                return VkApi.token_parser(page_role[1])
            elif page_role[0] == 4:
                logging.debug("Bad login")
                print("Указан неверный логин или пароль!")
                return tuple()
            elif page_role[0] == 6:
                logging.debug("Unknown error")
                print("Неизвестная ошибка!")
                return tuple()
            else:
                url_from_page = page_role[1]
                response = browser.open(url_from_page)
                page_role = VkApi.response_role(response)

if __name__ == '__main__':
    print("This library can't be started manually!")
    print("Try to import it in your code! EX: auth(client_id, permissions)")
