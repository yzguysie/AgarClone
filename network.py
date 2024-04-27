import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.180"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.data = self.connect()

    def getData(self):
        return self.data

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(4096*4096))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096*4096))
        
        except socket.error as e:
            print(e)
