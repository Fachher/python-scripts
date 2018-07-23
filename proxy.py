import socket
from threading import Thread

ALL_INTERFACES = '0.0.0.0'
PACKET_SIZE = 4096
TARGET_SERVER = '192.168.178.54'

# ACCOUNT -> PROXY -> SSO


class Proxy2SSO(Thread):
    def __init__(self, host, port):
        super(Proxy2SSO, self).__init__()
        self.account = None # account client socket not known yet
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    def run(self):
        while True:
            data = self.server.recv(PACKET_SIZE)
            if data:
                print("[{}] <- {}".format(self.port, data[:100].encode('hex')))
                # do something here
                self.account.sendall(data)


class Account2Proxy(Thread):

    def __init__(self, host, port):
        super(Account2Proxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        self.account, addr = sock.accept()

    def run(self):
        while True:
            data = self.account.recv(PACKET_SIZE)
            if data:
                print ("[{}] -> {}".format(self.port, data[:100].encode('hex')))
                self.server.sendall(data)


class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("[proxy({})] setting up".format(self.port))
            self.a2p = Account2Proxy(self.from_host, self.port)
            self.p2s = Proxy2SSO(self.to_host, self.port)
            print("[proxy({})] connection established".format(self.port))
            self.a2p.server = self.p2s.server
            self.p2s.account = self.a2p.account

            self.a2p.start()
            self.p2s.start()

# 192.168.178.54 is the target server
master_server = Proxy(ALL_INTERFACES, TARGET_SERVER, 3333)
master_server.start()

Proxy(ALL_INTERFACES, TARGET_SERVER, 3000).start()