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

if __name__ == "__main__":
    node_1 = NodeUDP(1)
    node_2 = NodeUDP(2)
    node_1.send(b"i'm node 1", ("127.0.0.1", 10002))
    recieve_msg, _ = node_2.recv()
    print("1" in recieve_msg)
    