import select
import socket


def handle(c_conn: socket.socket, addr, logger):
    msg_buffer = bytearray()
    header_end = -1
    while header_end == -1:
        # read until we find the end of the header
        try:
            data = c_conn.recv(4096)
        except OSError as e:
            logger.error(f"failed to read from client: {e}")
            c_conn.close()
            return
        if not data:  # client closed connection, stop reading
            c_conn.close()
            logger.info(f"client closed connection")
            return
        msg_buffer.extend(data)
        header_end = msg_buffer.find(b'\r\n\r\n')
    header = msg_buffer[:header_end]
    first_line = header.partition(b'\r\n')[0]
    fields = first_line.split(b' ')
    if len(fields) != 3:
        logger.error(f"invalid request {first_line.decode('utf-8')}")
        c_conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
        c_conn.close()
        return
    verb, path, version = fields
    if version != b'HTTP/1.1':
        logger.error(f"unknown HTTP version in {first_line.decode('utf-8')}")
        c_conn.sendall(b'HTTP/1.0 505 HTTP Version Not Supported\r\n\r\n')
        c_conn.close()
        return
    if verb == b'GET' or verb == b'POST':
        # find field 'host' in the header
        host_line = next((f for f in header.split(b'\r\n') if f.lower().startswith(b'host:')))
        host_field = host_line[5:].strip()
        if not host_field:
            logger.error(f"missing host field")
            c_conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
            c_conn.close()
            return
        logger.info(f"{verb.decode('utf-8')} request for {path.decode('utf-8')}")
        handle_get(c_conn, host_field.decode('utf-8'), msg_buffer, logger)
    elif verb == b'CONNECT':
        logger.info(f"CONNECT request for {path.decode('utf-8')}")
        handle_connect(c_conn, path.decode('utf-8'), logger)
    else:
        logger.error(f"unknown request verb {verb}")
        c_conn.close()
        return


def handle_connect(c_conn: socket.socket, path: str, logger):
    try:
        hostname, port = path.split(':')
        port = int(port)
    except ValueError:
        logger.error(f"invalid CONNECT request path {path}")
        c_conn.sendall(b'HTTP/1.0 400 Bad Request\r\n\r\n')
        c_conn.close()
        return

    # open a connection to the remote host
    try:
        s_conn = socket.create_connection((hostname, port))
    except OSError:
        logger.error(f"failed to connect to remote host {hostname}:{port}")
        c_conn.sendall(b'HTTP/1.0 502 Bad Gateway\r\n\r\n')
        c_conn.close()
        return

    logger.info(f"connected to remote host {hostname}:{port}")
    c_conn.sendall(b'HTTP/1.0 200 OK\r\n\r\n')
    forward(c_conn, s_conn, logger)


def handle_get(c_conn: socket.socket, host: str, request: bytearray, logger):
    hostname, _, port = host.partition(':')
    port = int(port) if port else 80
    try:
        s_conn = socket.create_connection((hostname, port))
    except OSError:
        logger.error(f"failed to connect to remote host {hostname}:{port}")
        c_conn.sendall(b'HTTP/1.0 502 Bad Gateway\r\n\r\n')
        c_conn.close()
        return
    
    logger.info(f"connected to remote host {hostname}:{port}")
    s_conn.sendall(request)
    forward(c_conn, s_conn, logger)


def forward(c_conn: socket.socket, s_conn: socket.socket, logger):
    # forward data bi-directionally using select
    # until one of the connections is closed, close the other one
    while True:
        try:
            r, w, x = select.select([c_conn, s_conn], [], [])
            if c_conn in r:
                data = c_conn.recv(4096)
                if not data:
                    s_conn.close()
                    logger.info(f"client closed connection")
                    break
                s_conn.sendall(data)
            if s_conn in r:
                data = s_conn.recv(4096)
                if not data:
                    c_conn.close()
                    logger.info(f"server closed connection")
                    break
                c_conn.sendall(data)
        except OSError as e:
            # if any exception occurs, close both connections
            if c_conn.fileno() != -1:
                c_conn.close()
            if s_conn.fileno() != -1:
                s_conn.close()
            logger.info(f"connection closed due to exception{e}")
            break
