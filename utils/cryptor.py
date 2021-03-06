import hashlib
import base64
from Crypto.Cipher import AES


class AESEncrypt:
    def __init__(self, message, key):
        self.message = message
        self.key = key

    def __str__(self):
        return str(self.message)

    @staticmethod
    def _pad(blocked_string, block_size):
        """
        дополняет блок до кратного размерности
        """
        return blocked_string\
            + (block_size - len(blocked_string) % block_size)\
            * chr(block_size - len(blocked_string) % block_size)

    @staticmethod
    def _unpad(unblock_string):
        """
        отрезает излишки блока
        """
        return unblock_string[:-ord(unblock_string[len(unblock_string) - 1:])]

    @staticmethod
    def _md5(text):
        hasher = hashlib.md5()
        hasher.update(bytes(text, "utf-8"))
        return hasher.digest()

    @staticmethod
    def _cryption(string, password, encrypt_it=False):
        block_size = 16
        init_vector = "some bad or not text"[:block_size]  # TODO FIX КОСТЫЛЬ!
        cryptor = AES.new(password, AES.MODE_CBC, init_vector)
        if encrypt_it:
            return cryptor.encrypt(string)
        else:
            return cryptor.decrypt(string)

    def encrypt(self):
        line = self.message
        password = self.key
        line = self._pad(line, 16)
        adopted_pas = self._md5(password)
        crypted_bytes = self._cryption(line, adopted_pas, encrypt_it=True)
        return base64.b64encode(crypted_bytes)

    def decrypt(self):
        """
        Дешифрует base64 кодированную строку по заданному паролю:
        возвращает пустую строку при ошибке дешифрования
        (корректность определяется по попытке преобразовать в utf-8),
        непустую строку, при успешном дешифровании
        """
        line = self.message
        password = self.key
        debased = base64.b64decode(line)
        adopted_pas = self._md5(password)
        decrypted = self._cryption(debased, adopted_pas)
        try:
            cooked_string = self._unpad(decrypted).decode()
        except UnicodeDecodeError:
            raise AESEncryptError

        if cooked_string:
            return cooked_string
        else:
            raise AESEncryptError


class AESEncryptError(Exception):
    pass


if __name__ == '__main__':
    print("Nope, I am a lib!")
