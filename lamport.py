from NodeSocket import NodeUDP
from NodeSocket import startPort
from priorityqueue import PriorityQueue
import threading
import time
import queue
import logging
import random 
import multiprocessing
import sys

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("lamport")

node_num = 5
current = -1
enter_times = 10

message_type = ["request", "reply", "release"]

def str2tuple(s):
    # "<1,2>" -> (1,2) 
    return (int(s.split(',')[0][1:]), int(s.split(',')[1][:-1]))

def tuple2str(t):
    # (1,2) -> "<1,2>"
    return "<{},{}>".format(t[0], t[1])


class Node():
    def __init__(self, node_id):
        self.node_id = node_id
        self.timestamp = 0
        self.nodeudp = NodeUDP(node_id)
        self.thread = threading.Thread(target=self.listen, args=())
        self.thread.setDaemon(True)
        self.lock = threading.Lock()
        self.thread.start()
        self.q = PriorityQueue()
        self.q_lock = threading.Lock()
        self.replied_list = []
        self.reply_lock = threading.Lock()
        
        
    
    def send_to(self, message, node_id):
        self.lock.acquire()
        self.timestamp += 1
        message = "<{},{}>:".format(self.timestamp, self.node_id) + message
        logger.debug("node {} sends '{}' to node {} at {}".format(self.node_id, message, node_id, self.timestamp))
        self.lock.release()
        self.nodeudp.send(message, ("127.0.0.1", startPort+node_id))
    
    def broadcast(self, message):
        global node_num

        self.lock.acquire()
        self.timestamp += 1
        request_str = "<{},{}>".format(self.timestamp, self.node_id)
        message = "<{},{}>:".format(self.timestamp, self.node_id) + message
        logger.debug("node {} broadcasts '{}' at {}".format(self.node_id, message, self.timestamp))
        self.lock.release()

        for node_id in range(node_num):
            if node_id == self.node_id:
                continue
            self.nodeudp.send(message, ("127.0.0.1", startPort+node_id))
        
        return request_str
    

    def request(self):
        request_str = self.broadcast("request")
        request_tuple = str2tuple(request_str)
        self.q_lock.acquire()
        self.q.push(request_tuple)
        self.q_lock.release()

    def reply(self, request_str, to):
        self.send_to("reply:"+request_str, to)
    
    def release(self):
        self.broadcast("release")
        self.reply_lock.acquire()
        self.replied_list = []
        self.reply_lock.release()
        self.q_lock.acquire()
        self.q.pop()
        self.q_lock.release()
    
    def run(self):
        global enter_times
        global current
        global node_num
        for _ in range(enter_times):
            logger.info("node {} requests to enter CS".format(self.node_id))
            self.request()
            while True:
                time.sleep(0.1)
                self.q_lock.acquire()
                top_request_tuple = self.q.get()
                # self.q.put(top_request_tuple)
                self.q_lock.release()
                self.reply_lock.acquire()
                reply_num = len(self.replied_list)
                self.reply_lock.release()
                if self.node_id == top_request_tuple[1] and reply_num == (node_num-1):
                    break
            logger.info("node {} enters CS".format(self.node_id))
            time.sleep(random.randint(1,5))
            self.release()
            logger.info("node {} leaves CS".format(self.node_id))

    
    def listen(self):
        while True:
            msg = self.nodeudp.recv()[0]
            ts = int(msg.split(',')[0][1:])
            node_id = int(msg.split(',')[1].split('>')[0])
            if ts > self.timestamp:
                self.lock.acquire()
                self.timestamp = ts+1
                self.lock.release()
            else:
                self.lock.acquire()
                self.timestamp += 1
                self.lock.release()
            
            logger.debug("node {} recieve '{}' from node {} at {}".format(self.node_id, msg, node_id, self.timestamp))

            msg_type = msg.split(":")[1]
            if msg_type == "request":
                request_str = msg.split(":")[0]
                self.reply(request_str, node_id)
                request_tuple = str2tuple(request_str)
                self.q_lock.acquire()
                self.q.push(request_tuple)
                self.q_lock.release()
            elif msg_type == "reply":
                self.reply_lock.acquire()
                self.replied_list.append(node_id)
                self.reply_lock.release()
            elif msg_type == "release":
                self.q_lock.acquire()
                self.q.pop()
                self.q_lock.release()
            
            # logger.debug("node {}, queue: {}".format(self.node_id, self.q.queue))
            
            




    
if __name__ == "__main__":
    node_id = int(sys.argv[1])
    node = Node(node_id)
    time.sleep(5)
    node.run()

    '''
    Nodes = []
    Processes = []
    for node_id in range(node_num):
        Nodes.append(Node(node_id))
    for node_id in range(node_num):
        p = multiprocessing.Process(target=Nodes[node_id].run, )
        p.start()
        Processes.append(p)
    '''
    
