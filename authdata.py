import pickle
import logging

from utils.cryptor import AESEncrypt
from utils.cryptor import AESEncryptError

logger = logging.getLogger(__name__)


def _authdata_read(filename):
    """
    :param filename файл, откуда читать данные пользователя
    """
    try:
        with open(filename, "rb") as data_file:
            auth_info = pickle.load(data_file)
            return auth_info
    except FileNotFoundError:
        logger.debug("Auth file: \"{}\" not found!"
                     .format(filename))
        return {}
    except OSError:
        logger.debug("Can't reach {}".format(filename))
        return {}


def _authdata_write(auth_info, filename):
    """
    запись данных о пользователе в файл
    """
    try:
        with open(filename, "wb") as data_file:
            pickle.dump(auth_info, data_file)
        logger.debug("New auth file created!")
    except OSError:
        logger.debug("Can't reach {}".format(filename))


def write_tokens(social_id, master_key, user_info, data_file):
    """
    :param social_id:
    :param master_key:
    :param user_info:
    :param data_file:
    :return:
    """
    data = _authdata_read(data_file)
    for info_obj in user_info.keys():
        if "token" in info_obj:
            cryptor = AESEncrypt(user_info[info_obj], master_key)
            user_info[info_obj] = cryptor.encrypt()
    data[social_id] = user_info
    _authdata_write(data, data_file)


def get_tokens(social_id, master_key, data_file):
    read_array = _authdata_read(data_file)
    if social_id in read_array:
        current_interest = read_array[social_id]
        for key in current_interest.keys():
            if "token" in key:
                cryptor = AESEncrypt(current_interest[key], master_key)
                try:
                    current_interest[key] = cryptor.decrypt()
                except AESEncryptError:
                    current_interest = {}
        return current_interest
    else:
        return {}

if __name__ == '__main__':
    print("Nope, I am a lib!")
