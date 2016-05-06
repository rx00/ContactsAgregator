import getpass


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
                print("\nВы прервали ввод пароля! Выход из программы!")
                exit()
        else:
            try:
                string = input(output_text)
            except KeyboardInterrupt:
                print("\nВы прервали ввод строки! Выход из программы!")
                exit()
        if string == "":
            print("Поле", raw_text.lower(), "не может быть пустым!")
        else:
            return string


if __name__ == '__main__':
    print("Nope, I am a lib!")
