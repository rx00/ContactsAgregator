import datetime
import pickle

from utils.cryptor import AESEncrypt
from utils.cryptor import AESEncryptError


def authdata_read(filename="data"):
    """
    чтение данных о пользователе из файла
    """
    try:
        with open(filename, "rb") as f:
            auth_info = pickle.load(f)
            return auth_info
    except OSError:
        print("Нет доступа к файлу {}".format(filename))
        return {}


def authdata_write(auth_info, filename="data"):
    """
    запись данных о пользователе в файл
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(auth_info, f)
    except OSError:
        print("Нет доступа к файлу {}".format(filename))


def timestamp_get(timestamp=0):
    """
    при запуске без аргументов вернет текущее время (целое число)
    при запуске с аргументом (кол-во секунд), вернет (текущая дата + секунды из аргумента)
    """
    current_time = datetime.datetime.now()
    additional = datetime.timedelta(seconds=timestamp)
    timestamp = int((current_time + additional).timestamp())
    return timestamp


def write_vk_token(token, vk_id, masterkey, timestamp):
    """
    по ключу шифрует данные пользователя (его token)
    """
    cryptor = AESEncrypt(token, masterkey)
    good_token = cryptor.encrypt()
    time = timestamp_get(timestamp-1000)
    data = {"id": vk_id, "token": good_token, "timestamp": time}
    authdata_write(data)


def get_vk_token(masterkey):
    """
    по мастер-ключу восстанавливает непросроченный токен от ВКонтакте
    иначе возвращает пустую строку
    """
    data = authdata_read()
    if len(data) == 0:
        return {}
    else:
        if int(data["timestamp"]) > int(timestamp_get()):
            encrypted_token = data["token"]
            cryptor = AESEncrypt(encrypted_token, masterkey)
            try:
                token = cryptor.decrypt()
                data["token"] = token
                return data
            except AESEncryptError:
                return {}
        else:
            return {}
