import socket

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
        self.udp_send.sendto(message, addr)
    
    def recv(self):
        '''
        @return: (message, addr)
        '''
        message, addr = self.udp_listen.recvfrom(2048)
        return (message, addr)