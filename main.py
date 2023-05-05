import logging
import socket
import threading
from proxy import handle

port = 12345
host = ''
logfile = 'proxy.log'


def main():
    log_id = 1
    logging.basicConfig(
        filename=logfile,
        filemode='a',
        format='[%(log_id)6d]%(asctime)s %(levelname)s: %(message)s',
    )
    logger = logging.getLogger()
    logger.setLevel('INFO')
    logger.info(f'Starting proxy server', extra={'log_id': 0})
    try:
        # dummy proxy server that returns a fixed response
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
    except OSError as e:
        logger.error(f'Failed to start proxy server: {e}', extra={'log_id': 0})
        return
    else:
        logger.info(f'Proxy server listening on port {port}', extra={'log_id': 0})
    
    while True:
        conn, addr = s.accept()
        # make a logger with a unique id for each connection
        thread_logger = logging.LoggerAdapter(logger, {'log_id': log_id})
        threading.Thread(target=handle, args=(conn, addr, thread_logger)).start()
        log_id += 1


if __name__ == '__main__':
    main()
