import datetime
import pickle

from utils.cryptor import AESEncrypt


def authdata_read(filename="data"):
    """
    чтение данных о пользователе из файла
    получаем на вход имя файла
    """
    try:
        with open(filename, "rb") as f:
            auth_info = pickle.load(f)
            return auth_info
    except OSError:
        print("Нет доступа к файлу {}".format(filename))
        return ()


def authdata_write(auth_info, filename="data"):
    """
    запись данных о пользователе в файла
    получаем структуру данных и имя файла
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(auth_info, f)
    except OSError:
        print("Нет доступа к файлу {}".format(filename))


def authdata_create(social, userid, data, timestamp, password, file="tokenlist"):  # TODO выделить работу с авторизацией в класс

    user_string = social + ":"\
                  + userid + ":"\
                  + str(AESEncrypt.encrypt(data, password))[2:-1] + ":"\
                  + str(timestamp_get(timestamp))\
                  + "\n" # хрень, надо энкодить, а не в стринги гонять
    f = open(file, mode="a")
    f.write(user_string)


def authdata_get(password):
    f = open("tokenlist")
    line_list = f.readlines()
    auth_dump = line_list[0].split(":")
    f.close()
    user_id = auth_dump[1]
    token = auth_dump[2]
    timestamp = auth_dump[3]
    if timestamp > timestamp_get():
        decrypted_byte_token = decrypt(token, password)
        decrypted_token = str(decrypted_byte_token)[2:-1]
        return user_id, decrypted_token
    else:
        return ()


def timestamp_get(timestamp=0):
    """
    при запуске без аргументов вернет текущее время (целое число)
    при запуске с аргументом (кол-во секунд), вернет (текущая дата + секунды из аргумента)
    """
    current_time = datetime.datetime.now()
    additional = datetime.timedelta(seconds=timestamp)
    timestamp = int((current_time + additional).timestamp())
    return timestamp


def get_token(social):
    pass

  #  authdata_create("vk", "373645", "token=it's the token!", "86400", "123456")
  #  authdata_get()