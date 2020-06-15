import socket
import threading
from threading import Thread
import sys
from sys import stdin
import math
import time
import Queue



defaultPort = 9010
threads = [None] * 9
class node(object):
        def __init__ (self, identifier, cs_int, next_req, tot_exec_time, option):
            self.SelfCheckFlag = False
            self.t_listen = None
            self.selfIP = "127.0.0.1"
            self.identifier = int(identifier)
            self.port = defaultPort + self.identifier
            self.sock_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_listen.bind((self.selfIP, self.port))
            self.Stage = "Init"
            self.cs_int = int(cs_int)
            self.next_req = int(next_req)
            self.tot_exec_time = int(tot_exec_time)
            self.option = int(option)
            self.Request_ts = 0
            self.CurrAck = 0
            self.AckRecv = 0
            self.FailRecv = 0
            self.InquireRecv=0
            self.RepliedFlag = False
            self.RepliedNode = None
            self.RepliedTs = None
            self.RelinquishFlag = False
            self.Node_q = Queue.Queue()
            self.temp_q = Queue.Queue()
            self.tempts_q = Queue.Queue()
            self.ts_q = Queue.Queue()
            self.inCS = False
            self.ResCtr = 0
            self.Rsrdy = False
            
            self.tot_node_list = [1,2,3,4,5,6,7,8,9]
            if(self.identifier == 1):
                self.vote_set_list = [1,2,3,4,7]
            if(self.identifier == 2):
                self.vote_set_list = [1,2,3,5,8]
            if(self.identifier == 3):
                self.vote_set_list = [1,2,3,6,9]
            if(self.identifier == 4):
                self.vote_set_list = [1,4,5,6,7]
            if(self.identifier == 5):
                self.vote_set_list = [2,4,5,6,8]
            if(self.identifier == 6):
                self.vote_set_list = [3,4,5,6,9]
            if(self.identifier == 7):
                self.vote_set_list = [1,4,7,8,9]
            if(self.identifier == 8):
                self.vote_set_list = [2,5,7,8,9]
            if(self.identifier == 9):
                self.vote_set_list = [3,6,7,8,9]
            
        def start(self):
            time.sleep(2)
            #notify coordinator the node been created
            self.t_listen=threading.Thread(target=self.listen)
            self.t_listen.start()

            #init self check
            msg = "InitCheck " + str(self.identifier) 
            for i in range(0,5):
                self.send(msg, defaultPort + int(self.vote_set_list[i]))
            while(True):
                
                if(self.Stage == "Init" and self.SelfCheckFlag == True):
                    time.sleep(2)
                    self.Stage = "Request"
                    #print "Into Request Stage at Node " + str(self.identifier)
                
                elif(self.Stage == "Request"):
                    self.Request_ts = time.time() 
                    message = "Request " +str(self.identifier) + " " + str(self.Request_ts)
                    for i in range(0,5):
                        self.send(message, defaultPort + int(self.vote_set_list[i]))
                    self.Stage = "Request_wait"
                elif(self.Stage == "Request_wait"):
                    if(self.AckRecv == 5):
                        self.Stage = "Held"
                    

                            
        def listen(self):
            InitCheckCtr = 0;
            global defaultPort
            while True:
                msg, addr = self.sock_listen.recvfrom(1024) 
                if not msg:
                    continue
             
                message = msg.split(" ")
                size = len(message)
                message[0] = message[0].strip()
                
                if(message[0] == "InitCheck"):
                    message[1] = message[1].strip()
                    msg = "InitAck " + str(self.identifier) 
                    self.send(msg, defaultPort + int(message[1]))
                
                elif(message[0] == "InitAck"):
                    InitCheckCtr= InitCheckCtr + 1
                    if(InitCheckCtr == 5):
                        print "Self Check Complete, Node " + str(self.identifier) +"\n"
                        self.SelfCheckFlag = True
                        
                elif(message[0] == "Request"):
                   # if(self.identifier == 1):
                   #     print message[0] + " " + message[1]+ " " + message[2]
                    message[1] = message[1].strip()
                    message[2] = message[2].strip()
                    if(self.RepliedNode == None):
                        self.RepliedNode = int(message[1])
                        self.RepliedTs = float(message[2])
                        #if(self.identifier == 1):
                        #    print "[REQUEST] " + str(self.RepliedNode) + " " +str(self.RepliedTs)
                        msg = "Grant " + str(self.identifier)
                        self.send(msg, defaultPort + int(message[1]))

                    elif(self.RepliedNode != None):
                        #if the coming message has a larger timestamp. Send failed back to requestor. But still queue request in priority queue
                        if(self.RepliedTs < float(message[2])):
                            #msg = "Fail " + str(self.identifier)
                            #self.send(msg, defaultPort + int(message[1]))
                            self.Node_q.put(int(message[1]))
                            self.ts_q.put(float(message[2]))
                            #print "[Failed]send to " + str(message[1])
                        elif(self.RepliedTs == float(message[2])):
                            if(self.RepliedNode < int(message[1])):
                                #msg = "Fail " + str(self.identifier)
                                #self.send(msg, defaultPort + int(message[1]))
                                self.Node_q.put(int(message[1]));
                                self.ts_q.put(float(message[2]))
                            else:
                                msg = "Inquire " + str(self.identifier)
                                self.send(msg, defaultPort + self.RepliedNode)
                                self.Node_q.put(int(message[1]))
                                self.ts_q.put(float(message[2]))
                        elif(self.RepliedTs > float(message[2])):
                            msg = "Inquire " + str(self.identifier)
                            self.send(msg, defaultPort + self.RepliedNode)
                            self.Node_q.put(int(message[1]))
                            self.ts_q.put(float(message[2]))


                
                #elif(message[0] == "Fail"):
                #        self.FailRecv= self.FailRecv+1
                #        if(self.FailRecv >0 and self.InquireRecv >0):
                #            print "[Abort] at node: "+ str(self.identifier)

                elif(message[0] == "Inquire"):
                        if((self.inCS == False) and (self.Rsrdy == False)):                      
                            self.AckRecv =0
                            msg = "Rescind " + str(self.identifier)
                            print "Recived Inquire, now rescind at node: " + str(self.identifier)
                            self.Rsrdy = True
                            for i in range(0,5):
                                    self.send(msg, defaultPort + int(self.vote_set_list[i]))
                
                elif(message[0] == "Rescind"):
                        
                        message[1] = message[1].strip()
                        print "Rescind received for " + str(message[1]) + " at " + str(self.identifier)
                        msg = "ResAck"
                        self.send(msg, defaultPort +int(message[1]))
                        print "REPLY to " + str(message[1])+ " at node " +str(self.identifier)
                        if(self.RepliedNode == int(message[1])):
                            next1 = int(self.Node_q.get())
                            next_ts = float(self.ts_q.get())
                            self.RepliedNode = next1
                            self.RepliedTs = next_ts
                            msg = "Grant " + str(self.identifier)
                            self.send(msg, defaultPort + next1)
                        else:
                            while not self.Node_q.empty():
                                print "Hello " + str(self.Node_q.qsize())
                                temp = int(self.Node_q.get())
                                temp_ts = float(self.ts_q.get())
                                if(temp!=int(message[1])):
                                    self.temp_q.put(temp)
                                    self.tempts_q.put(temp_ts)
                                    
                            self.Node_q = self.temp_q
                            self.ts_q = self.tempts_q
                            while not self.temp_q.empty():
                                print "loop"
                                self.temp_q.get()
                                self.tempts_q.get()
                            
                elif(message[0] == "ResAck"):
                        self.ResCtr = self.ResCtr + 1
                        print "ResCtr at node " + str(self.identifier) + " is : " + str(self.ResCtr)
                        if(self.ResCtr == 5):
                            print "ResAck complete, now restart at node: " + str(self.identifier)
                            self.ResCtr = 0
                            self.Rsrdy = False
                            self.AckRecv =0
                            self.Request_ts = time.time() 
                            message = "Request " +str(self.identifier) + " " + str(self.Request_ts)
                            for i in range(0,5):
                                    self.send(message, defaultPort + int(self.vote_set_list[i]))                 
                                
                        #self.InquireRecv = self.InquireRecv+1
                        #if(self.FailRecv >0 and self.InquireRecv >0):
                        #    print "[Abort] at node: "+ str(self.identifier)
                elif(message[0] == "Grant"):
                        message[1] = message[1].strip()
                        self.AckRecv = self.AckRecv +1
                        
                        print "[RECV GRANT] recv grant from " + message[1] + " at node: " + str(self.identifier)
                        if(self.AckRecv == 5):
                            self.inCS = True
                            print "[Grant] going to CS at node: " + str(self.identifier)
                    
                            
                
                    
        
        def send(self, message, port):
            self.sock_send.sendto(message, (self.selfIP, port))      
                
                
                
class maekawa(object):
    def __init__(self, argument):
        argv = argument.split(" ")
        
        global defaultPort
        self.selfIP = "127.0.0.1"
        self.num_node = 9
        self.cs_int = int(argv[0].strip())
        self.next_req = int(argv[1].strip())
        self.tot_exec_time = int(argv[2].strip())
        self.option = int(argv[3].strip())
        
    def start(self):
        #directly invoke the node 0
        for i in range (1, 10):
            defaultNode = node(str(int(i)), str(self.cs_int), str(self.next_req), str(self.tot_exec_time), str(self.option))
            thread = threading.Thread(target=defaultNode.start)
            thread.start()       
            threads[i-1] = thread
        currentTime = time.time()
        targetTime = currentTime + self.tot_exec_time
        while(time.time()<targetTime):
            continue
        print "Total Execute Time reached. Program now exiting!"
        exit()


if __name__ == '__main__':
    if len(sys.argv) <5:
            sys.argv.append(raw_input('Maekawa> Please type in the argument in this order: <cs_int> <next_req> <tot_exec_time> <option>\n'))
            print sys.argv[1]
    maekawa = maekawa(sys.argv[1])
    maekawa.start()
