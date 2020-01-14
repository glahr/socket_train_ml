# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:15:27 2020

@author: griloHBG
"""
import socket
from enum import Enum, auto


# enumeration for message types. used to differentiate between what server and client are communicating
class TCPMessageType(Enum):
    ACK = auto()
    MODEL_REQUEST = auto()
    MEMORY_REQUEST = auto()
    
# class for specific communication for KR16 robot learning
class TCPConnection:
    
    def __init__(self, ip, port, is_server=False, reusable=True, buffer_size=1024):
        # stores server's IP for both server and client object 
        self._ip = ip
        # stores server's PORT for both server and client object 
        self._port = port
        # defines if this object is for a server or a client
        self._is_server = is_server
        # stores if this object's socket will be reusable
        self._reusable = reusable
        # buffer_size for receiving messages
        self._buffer_size = buffer_size
        
        # if this is the server
        if self._is_server:
            # bind application, port and ip
            self._socket.bind((self._ip,self._port))
        
            # creates the server socket that listens for incomming connection requests
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
        
            # creates the client socket that requests connection on the server
            self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # set socket to non-blocking mode
            # TODO: does this even work?
            self._connection.setblocking(False)

                            #########################
                            #                       #
#############################   INTERNAL FUNCTIONS  ###########################
                            #                       #
#############################          init         ###########################
                            #                       #
                            #########################
    
    # internal receive function 
    def _recv(self, msg_total_size=0):
        # stores the full message
        total_msg = []
        # indicates how much bytes already received
        bytes_received = 0
        
        # while all expected bytes weren't received
        while bytes_received < max(msg_total_size, self._buffer_size):
            # receive the remaining
            partial_msg = self._connection.recv(min(msg_total_size - bytes_received, self._buffer_size))
            # if none received
            if partial_msg == b'':
                # ERROR!
                raise RuntimeError("_recv - socket connection broken")
            # append to the array
            total_msg.append(partial_msg)
            # increase the amount of bytes received
            bytes_received = bytes_received + len(partial_msg)
        # return everything concatenated in a binary literal
        return b''.join(total_msg)
        
    # internal send function        
    def _send(self, data_bytes):
        # quantity of already sent bytes 
        sent_bytes = 0
        # while everything wasn't sent
        while sent_bytes < len(data_bytes):
            # send stuff
            sent = self._connection.send(data_bytes[sent_bytes:])
            # if none sent
            if sent == 0:
                # ERROR
                raise RuntimeError("_send - socket connection broken")
                return False
            # increase amount of bytes sent
            sent_bytes = sent_bytes + sent
        # return success
        return True

                            #########################
                            #                       #
#############################   INTERNAL FUNCTIONS  ###########################
                            #                       #
#############################           end         ###########################
                            #                       #
                            #########################

                            #########################
                            #                       #
#############################    SERVER FUNCTIONS   ###########################
                            #                       #
#############################          init         ###########################
                            #                       #
                            #########################
    
    
    # function to make server wait (blocked!) for a client connection
    def wait_client(self):
        # client should not use this function
        if not self._is_server:
            raise Exception('You\'re not a Server! Client can\'t wait for connection!')
            return
        # listen for incoming connection (only 1)
        self._socket.listen(1)
        # accpet connection, get who is the client (self._client) and the create connection socket (self._connection)
        self._connection, self._client = self._socket.accept()
        # print stuff
        #print('Received connection from',self._client)
        # return success
        return True
        
        
    
    # receive model (expected to client (training PC) send model update to server (KUKA controller PC))
    def recv_model_update(self):
        # send a model requisition
        self._send(TCPMessageType.MODEL_REQUEST)
        
        # receive the model size
        model_size = self._recv()
        
        # send a ack informing that size was received
        # TODO: do we really need this ACK?
        self._send(TCPMessageType.ACK)
        
        # receive model in bytes format (pickle, probably)
        model_bytes = self._recv(model_size)
        
        # return whatever was received
        return model_bytes
        
    # send real world traning output (expected to server (KUKA controller PC) send memoty update to client (training PC))
    def send_memory_update(self, memory_bytes):
        # send a memory sending requisition
        self._send(TCPMessageType.MEMORY_REQUEST)
        
        # receive a ACK
        # TODO: do we really need this ACK?
        msg = self._recv()
        # if no ACK received...
        if not msg == TCPMessageType.ACK:
            # ERROR!
            raise Exception('ACK expected. Received instead:', msg)
            return
        
        # send memory size
        self._send(len(memory_bytes))
        
        # sendo memory
        self._send(memory_bytes)

                            #########################
                            #                       #
#############################    SERVER FUNCTIONS   ###########################
                            #                       #
#############################           end         ###########################
                            #                       #
                            #########################

                            #########################
                            #                       #
#############################    CLIENT FUNCTIONS   ###########################
                            #                       #
#############################          init         ###########################
                            #                       #
                            #########################
    
    # function to client request connection to server
    def connect_to_server(self):
        # server should not use this function
        if self._is_server:
            raise Exception('You\'re a Server! Server can\'t request connection!')
            return
        # request connection to server
        self._connection.connect((self._ip, self._port))
    # try send model (expected to client (training PC) send model update to server (KUKA controller PC))
    def try_send_model_update(self, model_bytes):
        
        # receive a model receiving requisition message
        msg = self._recv()
        
        # client's socket (self._connection) is non-blocking, so we may receive nothing!
        if msg == '':
            # return False in this case
            return False
        
        # otherwise, evaluates to check if it is the expected message
        if not msg == TCPMessageType.MODEL_REQUEST:
            # if not, ERROR!
            raise Exception('MODEL_REQUEST expected. Received instead:', msg)
            return False
        
        # send model size
        self._send(len(model_bytes))
        
        #wait for ACK
        msg = None
        while msg == None:
            msg = self._recv()
            
        # if it is not a ACK
        # TODO: do we really need this ACK?
        if not msg == TCPMessageType.ACK:
            # ERROR!
            raise Exception('ACK expected. Received instead:', msg)
            return False
        
        # finally send the model!
        self._send(model_bytes)
        
        # return success!
        return True
        

    
    # try receive real world traning output (expected to server (KUKA controller PC) send memoty update to client (training PC))
    def try_recv_memory_update(self):
        
        # receive a memory sending requisition message
        msg = self._recv()
        
        # client's socket (self._connection) is non-blocking, so we may receive nothing!
        if msg == '':
            return False
        
        # otherwise, evaluates to check if it is the expected message
        if not msg == TCPMessageType.MEMORY_REQUEST:
            # if not, ERROR!
            raise Exception('MEMORY_REQUEST expected. Received instead:', msg)
            return
        
        
        # send a ack informing that size was received
        # TODO: do we really need this ACK?
        self._send(TCPMessageType.ACK)
        
        # client's socket (self._connection) is non-blocking, so we may receive nothing!
        # then poll for reception!
        memory_size = None
        while memory_size == None:
            memory_size = self._recv()
            
        
        # client's socket (self._connection) is non-blocking, so we may receive nothing!
        # then poll for reception!
        memory_bytes = None
        while memory_bytes == None:
            memory_bytes = self._recv(memory_size)
        
        # return da stuff
        return memory_bytes
                            #########################
                            #                       #
#############################    CLIENT FUNCTIONS   ###########################
                            #                       #
#############################           end         ###########################
                            #                       #
                            #########################
       

        