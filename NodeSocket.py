import socket
from select import select

node_num = 3
startPort = 10000
class NodeUDP(object):
    def __init__(self, nodeId):
        self.IP = "0.0.0.0"
        self.port = startPort + nodeId
        self.udp_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_listen.bind((self.IP, self.port))
        self.udp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message, addr):
        '''
        message for send,
        addr is (IP, port)
        '''
        messageBytes = message.encode('gbk')
        self.udp_send.sendto(messageBytes, addr)
    
    def recv(self):
        '''
        @return: (message, addr)
        '''
        message, addr = self.udp_listen.recvfrom(2048)
        return (message.decode('gbk'), addr)

class NodeTCP(object):
    def __init__(self, nodeId):
        self.IP = "0.0.0.0"
        self.port = startPort + nodeId
        self.tcp_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_listen.bind((self.IP, self.port))
        self.tcp_send = []
        while len(self.tcp_send) < nodeId:
            self.tcp_send.append(self.tcp_listen.accept()[0])
        for i in range(nodeId + 1, node_num):
            socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_send.connect(("127.0.0.1", startPort + i))
            self.tcp_send.append(socket_send)
    
    def send(self, message, addr):
        messageBytes = message.encode('gbk')
        self.tcp_send[addr[1] - startPort].send(messageBytes)
    
    def recv(self):
        readable, _, _ = select(self.tcp_send, [], [])
        for sock in readable:
            message = sock.recv(2048)
            return message.decode('gbk'), None

if __name__ == "__main__":
    node_1 = NodeTCP(0)
    node_2 = NodeTCP(1)
    while (True):
        to_send = "hahaha"
        node_1.send(to_send, ("127.0.0.1", 10001))
        print(node_2.recv())
    