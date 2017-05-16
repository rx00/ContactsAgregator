import socket
import webbrowser


def open_web_browser(client_id, permissions, port=8087):
    url = "https://oauth.vk.com/authorize?" \
          "redirect_uri=0.0.0.0:{}" \
          "&response_type=token" \
          "&client_id={}" \
          "&scope={}" \
          "&display=page" \
          "&v=5.64".format(port, client_id, permissions)
    webbrowser.open(url)


def socket_auth():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 8087))
    sock.listen(1)
    conn, _ = sock.accept()
    data = conn.recv(2048)
    conn.send(b'HTTP/1.1 200 OK\nContent-Type: text/html\n\n '
              b'<html><body><script>'
              b'function sendIt() {'
              b'xmlHttp = new XMLHttpRequest();'
              b'xmlHttp.open( "GET", "http://0.0.0.0:8086/" + window.location.hash.substr(1), false);'
              b'xmlHttp.send( null );'
              b'}'
              b'setTimeout(sendIt, 1000);'
              b'</script><center><h1>YEP!</h1>Your token has been successfully sent!</center></body></html>')
    conn.close()
    sock.close()
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 8086))
    sock.listen(1)
    conn, _ = sock.accept()
    data = conn.recv(2048)
    conn.send(b'HTTP/1.0 200 OK\nContent-Type: text/html\n\n OK')
    conn.close()
    sock.close()
    return data


def token_extractor(data):
    user_id = data.decode().split()[1].split("=")[3]
    token = data.decode().split('&')[0].split('=')[1]
    return {"token": token, "id": user_id}


def authorize(client_id, permissions="groups,status,wall,offline"):
    open_web_browser(client_id, permissions)
    return token_extractor(socket_auth())