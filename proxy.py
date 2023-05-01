import socket

port = 12345
host = ''

# dummy proxy server that returns a fixed response
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print('Connected by', addr)
        data = conn.recv(1024)
        print(data)
        conn.sendall(b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>hello world</h1>')
        conn.close()


if __name__ == '__main__':
    main()