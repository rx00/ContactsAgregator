import sys
from PyQt5.QtWidgets import \
    QApplication, QWidget, QDesktopWidget, QLabel, QLineEdit, QPushButton
from PyQt5 import QtGui
from PyQt5.QtCore import QThread
from authlibs import vklib, twitterlib
import webbrowser


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.active_elements = {}
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
            pixmap = QtGui.QPixmap("logo.png")
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
                gui["vk_user_field_box"].deleteLater()
                gui["vk_pass_field_box"].deleteLater()
                gui["vk_auth_button"].deleteLater()
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
        self.active_elements["vk_auth"]["send_code_button"].deleteLater()
        self.active_elements["vk_auth"]["vk_pass_code"].deleteLater()
        self.active_elements["vk_auth"]["logo_box"].deleteLater()

        self.active_elements["vk_auth"].clear()
        self.active_elements["tw_auth"] = {}
        gui = self.active_elements["tw_auth"]
        self.setStyleSheet("background-color: #1da0f2")
        gui["tw_auth"] = {}
        twitter_label = QLabel(self)
        twitter_label.setPixmap(QtGui.QPixmap("tw.png"))
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
        gui["twitter_run_auth"].deleteLater()
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
        print(self.twitter.oauth_token_secret)


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
