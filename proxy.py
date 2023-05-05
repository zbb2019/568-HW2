import select
import socket


def handle(c_conn: socket.socket, addr):
    msg_buffer = bytearray()
    header_end = -1
    while header_end == -1:
        # read until we find the end of the header
        data = c_conn.recv(4096)
        if not data:  # client closed connection, stop reading
            return
        msg_buffer.extend(data)
        header_end = msg_buffer.find(b'\r\n\r\n')
    header = msg_buffer[:header_end]
    first_line = header.partition(b'\r\n')[0]
    fields = first_line.split(b' ')
    if len(fields) != 3:
        print('invalid request')
        c_conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
        c_conn.close()
        return
    verb, path, version = fields
    if version != b'HTTP/1.1':
        print(f"unknown HTTP version {version}")
        c_conn.sendall(b'HTTP/1.0 505 HTTP Version Not Supported\r\n\r\n')
        c_conn.close()
        return
    if verb == b'GET' or verb == b'POST':
        # find field 'host' in the header
        host_line = next((f for f in header.split(b'\r\n') if f.lower().startswith(b'host:')))
        host_field = host_line[5:].strip()
        if not host_field:
            print('missing host field')
            c_conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
            c_conn.close()
            return
        print(f"GET request for {path.decode('utf-8')}")
        handle_get(c_conn, host_field.decode('utf-8'), msg_buffer)
    elif verb == b'CONNECT':
        print(f"CONNECT request for {path.decode('utf-8')}")
        handle_connect(c_conn, path.decode('utf-8'))
    else:
        print(f"unknown request verb {verb}")
        c_conn.close()
        return


def handle_connect(c_conn: socket.socket, path: str):
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
    forward(c_conn, s_conn)


def handle_get(c_conn: socket.socket, host: str, request: bytearray):
    hostname, _, port = host.partition(':')
    port = int(port) if port else 80
    try:
        s_conn = socket.create_connection((hostname, str(port)))
    except OSError:
        print(f"failed to connect to remote host {hostname}:{port}")
        c_conn.sendall(b'HTTP/1.0 502 Bad Gateway\r\n\r\n')
        c_conn.close()
        return
    
    print(f"connected to remote host {hostname}:{port}")
    s_conn.sendall(request)
    forward(c_conn, s_conn)


def forward(c_conn: socket.socket, s_conn: socket.socket):
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
