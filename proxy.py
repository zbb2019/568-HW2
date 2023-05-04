import select
import socket


def handle(conn: socket.socket, addr):
    msg_buffer = bytearray()
    header_end = -1
    while header_end == -1:
        # read until we find the end of the header
        data = conn.recv(4096)
        if not data:  # client closed connection, stop reading
            return
        msg_buffer.extend(data)
        header_end = msg_buffer.find(b'\r\n\r\n')
    header = msg_buffer[:header_end]
    first_line = header.partition(b'\r\n')[0]
    fields = first_line.split(b' ')
    if len(fields) != 3:
        print('invalid request')
        conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
        conn.close()
        return
    verb, path, version = fields
    if version != b'HTTP/1.1':
        print(f"unknown HTTP version {version}")
        conn.sendall(b'HTTP/1.0 505 HTTP Version Not Supported\r\n\r\n')
        conn.close()
        return
    if verb == b'GET':
        print(f"GET request for {path.decode('utf-8')}")
        conn.sendall(
            b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>hello world</h1>')
        conn.close()
    elif verb == b'CONNECT':
        print(f"CONNECT request for {path.decode('utf-8')}")
        handle_connect(conn, path.decode('utf-8'))
    else:
        print(f"unknown request verb {verb}")
        conn.close()
        return


def handle_connect(c_conn: socket.socket, path: str):
    # path format: "hostname:port"
    try:
        hostname, port = path.split(':')
        port = int(port)
    except ValueError:
        print(f"invalid CONNECT request path {path}")
        c_conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
        c_conn.close()
        return
    
    # open a connection to the remote host
    try:
        s_conn = socket.create_connection((hostname, str(port)))
    except OSError:
        print(f"failed to connect to remote host {hostname}:{port}")
        c_conn.sendall(b'HTTP/1.0 502 Bad Gateway\r\n\r\n')
        c_conn.close()
        return
    
    print(f"connected to remote host {hostname}:{port}")
    c_conn.sendall(b'HTTP/1.0 200 OK\r\n\r\n')
    # forward data bi-directionally using select
    # until one of the connections is closed, close the other one
    while True:
        try:
            r, w, x = select.select([c_conn, s_conn], [], [])
            if c_conn in r:
                data = c_conn.recv(4096)
                if not data:
                    s_conn.close()
                    break
                s_conn.sendall(data)
            if s_conn in r:
                data = s_conn.recv(4096)
                if not data:
                    c_conn.close()
                    break
                c_conn.sendall(data)
        except OSError:
            # if any exception occurs, close both connections
            if c_conn.fileno() != -1:
                c_conn.close()
            if s_conn.fileno() != -1:
                s_conn.close()
            break
