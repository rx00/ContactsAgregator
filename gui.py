import sys
import webbrowser
from PyQt5.QtWidgets import \
    QWidget, QDesktopWidget, QLabel, QLineEdit, QPushButton
from PyQt5 import QtGui
from PyQt5.QtCore import QThread
from authlibs import vklib, twitterlib
from PyQt5.QtWidgets import QListWidget, QApplication, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from urllib.error import HTTPError


from vcardlib import Card
import utils.vk_parser
import utils.twitter_parser
from utils.twitter_parser import user_extractor


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.active_elements = {}
        self.card_list = []
        self.init_ui()

    def init_ui(self):
        self.resize(400, 500)
        self.setWindowTitle('Адресная книга')
        self.center()
        self.show()
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: #507299")
        self.show_vk_auth()

    def show_vk_auth(self, show=True):
        if show:
            try:
                if self.active_elements["vk_auth"]:
                    self.show_vk_auth(show=False)
            except KeyError:
                pass
            self.active_elements["vk_auth"] = {}
            gui = self.active_elements["vk_auth"]
            logo_box = QLabel(self)
            pixmap = QtGui.QPixmap("gui_images/logo.png")
            logo_box.setPixmap(pixmap)
            logo_box.move(108, 100)

            vk_user_field_box = QLineEdit(self)
            vk_user_field_box.setGeometry(100, 350, 200, 20)
            vk_user_field_box.setStyleSheet("background-color: #c0c0c0")
            vk_user_field_box.setPlaceholderText("Логин...")

            vk_pass_field_box = QLineEdit(self)
            vk_pass_field_box.setGeometry(100, 390, 200, 20)
            vk_pass_field_box.setStyleSheet("background-color: #c0c0c0")
            vk_pass_field_box.setEchoMode(QLineEdit.Password)
            vk_pass_field_box.setPlaceholderText("Пароль...")

            vk_auth_button = QPushButton(self)
            vk_auth_button.setGeometry(100, 430, 200, 20)
            vk_auth_button.setStyleSheet("background-color: #c0c0c0")
            vk_auth_button.setText("Авторизоваться!")
            vk_auth_button.clicked.connect(
                lambda _: self.run_auth(
                    vk_user_field_box.text(),
                    vk_pass_field_box.text()
                )
            )

            gui["logo_box"] = logo_box
            gui["vk_user_field_box"] = vk_user_field_box
            gui["vk_pass_field_box"] = vk_pass_field_box
            gui["vk_auth_button"] = vk_auth_button

            for element in gui.values():
                element.show()
        else:
            for element in self.active_elements["vk_auth"].values():
                try:
                    element.deleteLater()
                except RuntimeError:
                    pass
            self.active_elements["vk_auth"].clear()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def show_additional_fields(self):
        try:
            if self.api_obj._qt_thread_error:
                self.show_vk_auth()
                gui = self.active_elements["vk_auth"]
                label = QLabel(self)
                label.setText("Неверный логин или пароль!")
                label.setStyleSheet("font-family: Arial; color: red;")
                label.move(110, 300)
                label.show()
                gui["label"] = label
        except AttributeError:

            if self.api_obj.state == \
                    "Ожидание кода двухэтапной авторизации...":
                gui = self.active_elements["vk_auth"]
                try:
                    gui["vk_user_field_box"].deleteLater()
                    gui["vk_pass_field_box"].deleteLater()
                    gui["vk_auth_button"].deleteLater()
                except RuntimeError:
                    pass
                if "label" in gui:
                    gui["label"].deleteLater()
                vk_pass_code = QLineEdit(self)
                vk_pass_code.setStyleSheet("background-color: #c0c0c0")
                vk_pass_code.setGeometry(100, 390, 200, 20)
                vk_pass_code.show()

                send_code_button = QPushButton(self)
                send_code_button.setGeometry(100, 430, 200, 20)
                send_code_button.setStyleSheet("background-color: #c0c0c0")
                send_code_button.setText("Код двухэтапной авторизации")
                send_code_button.show()
                send_code_button.clicked.connect(
                    lambda _: self.run_two_step_auth(vk_pass_code.text())
                )
                gui["vk_pass_code"] = vk_pass_code
                gui["send_code_button"] = send_code_button
            else:
                if self.api_obj.token:
                    self.vk_object_ready()
                else:
                    self.show_vk_auth()

    def vk_object_ready(self):
        try:
            for element in self.active_elements["vk_auth"].values():
                try:
                    element.deleteLater()
                except RuntimeError:
                    pass
                except AttributeError:
                    pass
        except KeyError:
            pass

        if self.api_obj.state == "Ожидание кода двухэтапной авторизации...":
            self.show_additional_fields()
            return 0

        self.active_elements["vk_auth"].clear()
        self.active_elements["tw_auth"] = {}
        gui = self.active_elements["tw_auth"]
        self.setStyleSheet("background-color: #1da0f2")
        gui["tw_auth"] = {}
        twitter_label = QLabel(self)
        twitter_label.setPixmap(QtGui.QPixmap("gui_images/tw.png"))
        twitter_label.move(112, 100)
        twitter_label.show()

        twitter_agreement = QLabel(self)
        twitter_agreement.move(108, 310)
        twitter_agreement.setText(
            "Хотите ли Вы дополнительно\n авторизоваться в твиттере?"
        )
        twitter_agreement.setStyleSheet(
            "font-family: Arial; color: #ffffff;"
        )
        twitter_agreement.show()

        twitter_run_auth = QPushButton(self)
        twitter_run_auth.setGeometry(100, 400, 200, 20)
        twitter_run_auth.setText("Авторизоваться")
        twitter_run_auth.setStyleSheet("background-color: #c0c0c0")
        twitter_run_auth.show()
        twitter_run_auth.clicked.connect(self.twitter_obj_run)

        twitter_ignore_auth = QPushButton(self)
        twitter_ignore_auth.setGeometry(100, 440, 200, 20)
        twitter_ignore_auth.setText("Продолжить без авторизации")
        twitter_ignore_auth.setStyleSheet("background-color: #c0c0c0")
        twitter_ignore_auth.clicked.connect(self.ready)
        twitter_ignore_auth.show()

        gui["twitter_ignore_auth"] = twitter_ignore_auth
        gui["twitter_run_auth"] = twitter_run_auth
        gui["twitter_label"] = twitter_label
        gui["twitter_agreement"] = twitter_agreement

    def twitter_obj_run(self):
        gui = self.active_elements["tw_auth"]
        gui["twitter_ignore_auth"].deleteLater()
        gui["twitter_agreement"].deleteLater()
        gui["twitter_run_auth"].setText("Авторизуемся...")
        gui["twitter_run_auth"].setDisabled(True)
        self.twitter = twitterlib.TwitterApi(break_auth=True)
        self.api_thread = AuthObjectThread(self.twitter)
        self.api_thread.finished.connect(self.run_twitter_auth)
        self.api_thread.start()

    def run_twitter_auth(self):
        gui = self.active_elements["tw_auth"]
        try:
            gui["twitter_run_auth"].deleteLater()
        except RuntimeError:
            pass
        url = "https://api.twitter.com/oauth/authorize?oauth_token={}"\
            .format(self.twitter.oauth_token)
        webbrowser.open_new_tab(url)

        pin_code_field = QLineEdit(self)
        pin_code_field.setGeometry(100, 350, 200, 20)
        pin_code_field.setStyleSheet("background-color: #c0c0c0")
        pin_code_field.setPlaceholderText("Пин-код...")
        pin_code_field.show()
        pin_code_sender = QPushButton(self)
        pin_code_sender.setGeometry(100, 390, 200, 20)
        pin_code_sender.setStyleSheet("background-color: #c0c0c0")
        pin_code_sender.setText("Отправить пин-код")
        pin_code_sender.show()
        pin_code_sender.clicked.connect(
            lambda _: self.send_pin_code(pin_code_field.text())
        )

        gui["pin_code_sender"] = pin_code_sender
        gui["pin_code_field"] = pin_code_field

    def send_pin_code(self, code):
        gui = self.active_elements["tw_auth"]
        gui["pin_code_field"].setDisabled(True)
        gui["pin_code_sender"].setDisabled(True)
        self.api_thread = AuthObjectThread(self.twitter, code)
        self.api_thread.finished.connect(self.ready)
        self.api_thread.start()

    def ready(self):
        try:
            if self.twitter._qt_thread_error \
                    or not self.twitter.oauth_token_secret:
                try:
                    for element in self.active_elements["tw_auth"].values():
                        element.deleteLater()
                except RuntimeError:
                    pass
                self.run_twitter_auth()
                return 0
        except AttributeError:
            pass


        self.active_elements["main"] = {}
        gui = self.active_elements["main"]
        for element in self.active_elements["tw_auth"].values():
            try:
                element.deleteLater()
            except RuntimeError:
                pass
            except AttributeError:
                pass

        logo_box = QLabel(self)
        pixmap = QtGui.QPixmap("gui_images/download.png")
        logo_box.setPixmap(pixmap)
        logo_box.move(120, 100)
        logo_box.resize(200, 200)
        logo_box.show()
        gui["logo_box"] = logo_box

        self.setStyleSheet("background-color: #e2e2e2")

        load_friends_button = QPushButton(self)
        load_friends_button.setText("Начать загрузку контактов")
        load_friends_button.clicked.connect(self.run_friends_loading)
        load_friends_button.move(105, 350)
        load_friends_button.show()
        gui["load_friends_button"] = load_friends_button

    def show_contacts(self):
        gui = self.active_elements["main"]
        listWidget = QListWidget(self)
        listWidget.setGeometry(20,20, 360, 400)
        for element in gui.values():
            try:
                element.deleteLater()
            except RuntimeError:
                pass
        gui["listWidget"] = listWidget
        for card in self.card_list:
            list_name = "(Vk) " + card.first_name_en + card.last_name_en
            if card.twitter_domain:
                list_name = "(Twitter) "+list_name
            item = QListWidgetItem(list_name)
            pixmap = QPixmap()
            pixmap.loadFromData(card.pre_loaded_photo)
            icon = QIcon()
            icon.addPixmap(pixmap)
            item.setIcon(icon)
            listWidget.addItem(item)
        listWidget.show()
        export_button = QPushButton(self)
        export_button.setGeometry(100, 435, 200, 20)
        export_button.setStyleSheet("background-color: #c0c0c0")
        export_button.clicked.connect(self.export_contacts)
        export_button.setText("Экспортировать в *.vcf")
        export_button.show()
        gui["export_button"] = export_button

    def export_contacts(self):
        try:
            with open("cards.vcf", "w", encoding="utf-8") as card_storage:
                for card in self.card_list:
                    card_storage.write(
                        str(card)
                    )
        except OSError:
            print("Программа не может получить доступ к файлу {}!"
                  .format("cards.vcf"))
        app.quit()

    def run_friends_loading(self):
        load_label = QLabel(self)
        load_label.move(100, 310)
        gui = self.active_elements["main"]
        load_label.setText(
            "Начинаем загрузку Ваших контактов,\n      пожалуйста, ожидайте..."
        )
        load_label.setStyleSheet(
            "font-family: Arial;"
        )
        gui["load_label"] = load_label
        gui["load_friends_button"].setDisabled(True)
        gui["load_friends_button"].setText("Загружаем...")
        load_label.show()
        try:
            if self.twitter.oauth_token_secret:
                self.load_users_thread = \
                    LoadItemsThread(self.api_obj, self.card_list, self.twitter)
            else:
                self.load_users_thread = \
                    LoadItemsThread(self.api_obj, self.card_list)
        except AttributeError:
            self.load_users_thread = \
                LoadItemsThread(self.api_obj, self.card_list)

        self.load_users_thread.finished.connect(self.show_contacts)
        self.load_users_thread.start()

    def run_two_step_auth(self, code):
        gui = self.active_elements["vk_auth"]
        gui["vk_pass_code"].setDisabled(True)
        gui["send_code_button"].setDisabled(True)
        gui["send_code_button"].setText("Отправляем код...")
        self.api_thread = \
            AuthObjectThread(self.api_obj, self.api_obj.await_code + code)
        self.api_thread.finished.connect(self.vk_object_ready)
        self.api_thread.start()

    def run_auth(self, login, passw):
        gui = self.active_elements["vk_auth"]
        gui["vk_user_field_box"].setDisabled(True)
        gui["vk_pass_field_box"].setDisabled(True)
        gui["vk_auth_button"].setText("Авторизуемся...")
        gui["vk_auth_button"].setDisabled(True)
        self.api_obj = vklib.VkApi(await_code=True)
        self.api_obj.vk_login = login
        self.api_obj.vk_password = passw
        if not self.api_obj.vk_login or not self.api_obj.vk_password:
            self.api_obj._qt_thread_error = "Пустые поля!"
            self.show_additional_fields()
        else:
            self.api_thread = AuthObjectThread(self.api_obj, "")
            self.api_thread.finished.connect(self.show_additional_fields)
            self.api_thread.start()


class AuthObjectThread(QThread):
    def __init__(self, api, code_url=""):
        QThread.__init__(self)
        self.code_url = code_url
        self.api_object = api
        self.error = ""

    def __del__(self):
        self.wait()

    def run(self):
        try:
            self.api_object.auth(self.code_url)
        except vklib.VkApiError as e:
            self.api_object._qt_thread_error = str(e)
        except HTTPError as e:
            self.api_object._qt_thread_error = str(e)


class LoadItemsThread(QThread):
    def __init__(self, vk_api_obj, card_list_link, twitter=None):
        QThread.__init__(self)
        self.vk_api_obj = vk_api_obj
        self.card_list_link = card_list_link
        self.twitter = twitter

    def __del__(self):
        self.wait()

    def create_cards(self, contacts):
        for contact in contacts:
            self.card_list_link.append(Card(contact))

    def load_twitter(self):
        twitter_friends_json = self.twitter.get_friends()
        twitter_vk_ids = user_extractor(twitter_friends_json)
        for friend_id in twitter_vk_ids.keys():
            for card in self.card_list_link:
                twitter_vk = twitter_vk_ids[friend_id]["current_mined_vk"]
                if card.vk_domain == twitter_vk:
                    card.twitter_domain = \
                        twitter_vk_ids[friend_id]["current_domain"]

    def run(self):
        vk_fields = ("domain", "contacts", "photo_50")
        parsed_json = self.vk_api_obj.get_friends(vk_fields)
        raw_users = utils.vk_parser.filter_by_mobile(parsed_json)
        vk_contacts = utils.vk_parser.extract_correct_mobiles(raw_users)
        self.create_cards(vk_contacts)
        if self.twitter is not None:
            self.load_twitter()
        for card in self.card_list_link:
            card.preload_photo()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
