import hashlib
import base64

from Crypto.Cipher import AES


def pad(blocked_string, block_size):
    """
    дополняет блок до кратного размерности
    """
    return blocked_string\
           + (block_size - len(blocked_string) % block_size)\
           * chr(block_size - len(blocked_string) % block_size)


def unpad(unblock_string):
    """
    отрезает излишки блока
    """
    return unblock_string[:-ord(unblock_string[len(unblock_string) - 1:])]


def md5(text):
    hasher = hashlib.md5()
    hasher.update(bytes(text, "utf-8"))
    return hasher.digest()


def cryption(string, password, encrypt_it=False):
    block_size = 16
    init_vector = "some bad or not text"[:block_size]  # TODO дописать автогенератор вектора инициализации
    cryptor = AES.new(password, AES.MODE_CBC, init_vector)
    if encrypt_it:
        return cryptor.encrypt(string)
    else:
        return cryptor.decrypt(string)


def encrypt(line, password):
    line = pad(line, 16)
    adopted_pas = md5(password)
    crypted_bytes = cryption(line, adopted_pas, encrypt_it=True)
    return base64.b64encode(crypted_bytes)


def decrypt(line, password):
    """
    Дешифрует строку по заданному паролю:
    возвращает пустую строку при ошибке дешифрования(корректность определяется по попытке преобразовать в utf-8),
    непустую строку, при успешном дешифровании
    """
    debased = base64.b64decode(line)
    adopted_pas = md5(password)
    decrypted = cryption(debased, adopted_pas)
    try:
        return unpad(decrypted).decode()
    except UnicodeDecodeError:  # хрень, не работает, возвращает пустую строку при дешифровании
        print("Введен неверный ключ шифрования!")
        return ""


a = encrypt("line1", "some_password")
print(decrypt(a, "some_password"))
print(decrypt(a, "some_passworo"))
