import datetime
import pickle
import logging

from utils.cryptor import AESEncrypt
from utils.cryptor import AESEncryptError

logger = logging.getLogger(__name__)


def authdata_read(filename):
    """
    :param filename файл, откуда читать данные пользователя
    """
    try:
        with open(filename, "rb") as f:
            auth_info = pickle.load(f)
            return auth_info
    except FileNotFoundError:
        logger.debug("Файл данных авторизации \"{}\" не найден!"
                     .format(filename))
        return {}
    except OSError:
        logger.debug("Нет доступа к файлу {}".format(filename))
        return {}


def authdata_write(auth_info, filename):
    """
    запись данных о пользователе в файл
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(auth_info, f)
        print("Создан новый файл авторизации!")
        logger.debug("New auth file created!")
    except OSError:
        print("Нет доступа к файлу {}".format(filename))


def timestamp_get(timestamp=0):
    """
    при запуске без аргументов вернет текущее время (целое число)
    при запуске с аргументом (кол-во секунд), вернет
    (текущая дата + секунды из аргумента)
    """
    current_time = datetime.datetime.now()
    additional = datetime.timedelta(seconds=timestamp)
    timestamp = int((current_time + additional).timestamp())
    return timestamp


def write_tokens(social_id, master_key, user_info, data_file):
    data = authdata_read(data_file)
    for info_obj in user_info.values():
        if "token" in info_obj:
            cryptor = AESEncrypt(info_obj, master_key)
            user_info[info_obj] = cryptor.encrypt()
    data[social_id] = user_info
    authdata_write(data, data_file)


def get_tokens(social_id, master_key, data_file):
    read_array = authdata_read(data_file)
    if social_id in read_array:
        current_interest = read_array[social_id]
        for key in current_interest.values():
            if "token" in key:
                cryptor = AESEncrypt(key, master_key)
                try:
                    current_interest[key] = cryptor.decrypt()
                except AESEncryptError:
                    current_interest = {}
        return current_interest
    else:
        return {}

if __name__ == '__main__':
    print("Nope, I am a lib!")
