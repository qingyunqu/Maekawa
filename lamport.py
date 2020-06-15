from NodeSocket import NodeUDP
from NodeSocket import startPort
import threading
import time

client_num = 3

class Node():

    def __init__(self, node_id):
        self.node_id = node_id
        self.stop = False
        self.nodeudp = NodeUDP(node_id)
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.setDaemon(True)
        self.thread.start()
        
        
    
    def send_to(self, message, node_id):
        self.nodeudp.send(message, ("127.0.0.1", startPort+node_id))
    
    def broadcast(self, message):
        global client_num
        for i in range(client_num):
            if i == self.node_id:
                continue
            self.nodeudp.send(message, ("127.0.0.1", startPort+i))
    
    def run(self):
        while not self.stop:
            print(self.node_id, self.nodeudp.recv())
    
    def exit(self):
        self.stop = True


    
if __name__ == "__main__":
    Nodes = []
    for node_id in range(client_num):
        Nodes.append(Node(node_id))
    for node_id in range(client_num):
        Nodes[node_id].broadcast("I am node {}".format(node_id))
    time.sleep(1)
    # for node_id in range(client_num):
        # Nodes[node_id].exit()
