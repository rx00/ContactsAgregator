import datetime
import cryptor

def authdata_create(social, userid, data, timestamp, password, file="tokenlist"):  # TODO выделить работу с авторизацией в класс
    user_string = social + ":"\
                  + userid + ":"\
                  + str(cryptor.encrypt(data, password))[2:-1] + ":"\
                  + str(timestamp_get(timestamp))\
                  + "\n"
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
        decrypted_byte_token = cryptor.unpad(cryptor.decrypt(token, password))  # TODO пофиксить вечный вызов криптора
        decrypted_token = str(decrypted_byte_token)[2:-1]
        return user_id, decrypted_token
    else:
        return ()


def timestamp_get(timestamp=0):
    current_time = datetime.datetime.now()
    additional = datetime.timedelta(seconds=timestamp)
    timestamp = int((current_time + additional).timestamp())
    return timestamp


def get_token(social):
    pass

  #  authdata_create("vk", "373645", "token=it's the token!", "86400", "123456")
  #  authdata_get()