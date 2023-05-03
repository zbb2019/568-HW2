import socket
import threading

port = 12345
host = ''

def handle(conn, addr):
    msg_buffer = bytearray()
    header_end = -1
    while header_end == -1:
        # read until we find the end of the header
        data = conn.recv(4096)
        if not data: # client closed connection, stop reading
            return
        msg_buffer.extend(data)
        header_end = msg_buffer.find(b'\r\n\r\n')
    header = msg_buffer[:header_end]
    first_line = header.partition(b'\r\n')[0]
    fields = first_line.split(b' ')
    if len(fields) != 3:
        print('invalid request')
        conn.close()
        return
    verb, path, version = fields
    if version != b'HTTP/1.1':
        print(f"unknown HTTP version {version}")
        conn.close()
        return
    if verb == b'GET':
        print(f"GET request for {path.decode('utf-8')}")
        conn.sendall(b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>hello world</h1>')
        conn.close()
    else:
        print(f"unknown request verb {verb}")
        conn.close()
        return

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