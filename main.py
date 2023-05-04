import socket
import threading
from proxy import handle

port = 12345
host = ''


def main():
    # dummy proxy server that returns a fixed response
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    while True:
        result = s.accept()
        threading.Thread(target=handle, args=result).start()


if __name__ == '__main__':
    main()
