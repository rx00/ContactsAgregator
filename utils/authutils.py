import getpass
import sys

def text_caller(*args, private=False):
    """
    По принятому тексту инициализирует поток ввода
    поток ввода может быть опционально скрыт
    возвращает считанную строку
    """
    raw_text = args[0]
    output_text = raw_text + ": "
    string = ""
    while not string:
        if private:
            try:
                string = getpass.getpass(output_text)
            except KeyboardInterrupt:
                print("\nВы прервали ввод пароля!")
                exit_dialogue()
        else:
            try:
                string = input(output_text)
            except KeyboardInterrupt:
                print("\nВы прервали ввод строки!")
                exit_dialogue()
        if string == "":
            print("Поле", raw_text.lower(), "не может быть пустым!")
        else:
            return string


def exit_dialogue():
    print("Хотите выйти из программы? [Y/n]")
    string = input()
    if string == "" or string == "Y" or string == "y":
        sys.exit("DialogueInterrupt")


if __name__ == '__main__':
    print("Nope, I am a lib!")
