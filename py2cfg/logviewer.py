import logging
import pickle
import socket

logger = logging.getLogger(__name__)
logger.setLevel(1)


def main():
    with socket.socket(type=socket.SOCK_DGRAM) as sock:
        sock.bind(("", 8002))
        while True:
            logger.handle(
                logging.makeLogRecord(pickle.loads(sock.recv(2048)[4:]))
            )


if __name__ == "__main__":
    root = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(process)d - %(message)s"))
    root.addHandler(handler)
    main()
