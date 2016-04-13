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
            string = getpass.getpass(output_text)
        else:
            string = input(output_text)
        if string == "":
            print("Поле", raw_text.lower(), "не может быть пустым!")
        else:
            return string