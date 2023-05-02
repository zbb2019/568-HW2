import socket
import threading

port = 12345
host = ''

def handle(conn, addr):
    data = conn.recv(1024)
    print(data)
    conn.sendall(b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>hello world</h1>')
    conn.close()

# dummy proxy server that returns a fixed response
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    while True:
        result = s.accept()
        threading.Thread(target=handle, args=result).start()


if __name__ == '__main__':
    main()