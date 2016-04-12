import hashlib
import base64

from Crypto.Cipher import AES


def pad(blocked_string, block_size):
    return blocked_string\
           + (block_size - len(blocked_string) % block_size)\
           * chr(block_size - len(blocked_string) % block_size)


def unpad(unblock_string):
    return unblock_string[:-ord(unblock_string[len(unblock_string) - 1:])]


def md5(text):
    hasher = hashlib.md5()
    hasher.update(bytes(text, "utf-8"))
    return hasher.digest()


def cryption(string, password, encrypt_it=False):  # TODO запилить докстринги, поправить переменные
    BS = 16
    IV = "some bad or not text"[:BS]
    cryptor = AES.new(password, AES.MODE_CBC, IV)
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
    debased = base64.b64decode(line)
    adopted_pas = md5(password)
    decrypted = cryption(debased, adopted_pas)
    return unpad(decrypted)
