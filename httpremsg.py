import socket

class RecvError(Exception):
    pass


def parse_http_request(s: socket.socket):
    msg_buffer = bytearray()
    header_end = -1
    while header_end == -1:
        # read until we find the end of the header
        data = s.recv(4096)
        if not data:  # client closed connection, stop reading
            raise RecvError('client closed connection')
        msg_buffer.extend(data)
        header_end = msg_buffer.find(b'\r\n\r\n')
    header = msg_buffer[:header_end]
    first_line, _, header_fields = header.partition(b'\r\n')
    try:
        verb, path, version = first_line.split(b' ')
    except ValueError:
        return None
    header_dict = {}
    for field in header_fields.split(b'\r\n'):
        field = field.encode('utf-8').strip().lower()
        key, _, value = field.partition(b':')
        header_dict[key] = value.strip()
    if 'content-length' in header_dict:
        body = msg_buffer[header_end + 4:]
        while len(body) < int(header_dict['content-length']):
            data = s.recv(4096)
            if not data:
                raise RecvError('client closed connection')
            body.extend(data)
    

class HTTPRequest:
    verb: str = ''
    path: str = ''
    version: str = ''
    headers: bytes = b''
    body: bytes = b''
