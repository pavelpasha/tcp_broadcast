# -*- coding: utf-8 -*-
import time
import socket
import io
import threading
import select
import logging
import argparse


def try_close (socket):
    # type (socket.socket())
    try:
        socket.close()
    except:
        pass

class BroadcastServer ():
    def __init__ (self, input_port, broadcast_port):
        # type (int , int) -> None
        self.input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.input_port = input_port
        self.broadcast_port = broadcast_port
        self.work = True

    def start (self):
        threading.Thread(target=self._listen_for_clients, args=[], name="listen_clients").start()
        threading.Thread(target=self._broadcast, args=[], name="broadcast").start()
        logging.debug("Start listening on {0} port and broadcast to {1} port".format(self.input_port,self.broadcast_port))
    
    def stop (self):
        self.work = False

    def _broadcast (self):
        """
            The main thread. When input connection (data provider) will be accepted, "reading-broadcasting" loop will be start.
            But raised exceptions will breaks the loop so we will be able to accept new input connection
        """
        self.input_socket.bind(('',self.input_port))
        self.input_socket.listen(1)
        while self.work:
            input_conn, _ = self.input_socket.accept()
            input_conn.settimeout(30) # If connection with the input socket will be lost, and don`t closed properly, 
                                # we will never  know that. So we will be blocked in "recv" method forever. So we have to set 30 sec timeout.
                                # When timeout will be reached, an exception will be raised and breaks reading loop. 
                                # Sщ we will be able to accept an input connection again
            while self.work:
                try:
                    data = input_conn.recv(1024)
                    if not data:
                        raise Exception ("Connection is broken")
                    
                    for client in self.clients[:]:
                        try:
                            client.sendall(data)
                        except Exception as e:
                            logging.error("Error occured while sending data to client. Reason: {0}".format(e))
                            try_close(client)
                            self.clients.remove(client)
                except Exception as e:
                    try_close(input_conn) 
                    logging.error("Error occured while reading data. Reason: {0}".format(e))
                    break

    def _listen_for_clients (self):
        """
            Listen to clients and append it to list.
        """
        self.broadcast_socket.bind(('0.0.0.0',self.broadcast_port))
        self.broadcast_socket.listen(5)
        while self.work:
            connection, _ = self.broadcast_socket.accept()
            self.clients.append(connection)
            logging.debug("Client connected {0}".format(connection.getsockname()))


class PortAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 0 < values < 2**16:
            raise argparse.ArgumentError(self, "port numbers must be between 0 and 65535")
        setattr(namespace, self.dest, values)
  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="The port for input connection", default=200, action=PortAction, type = int)
    parser.add_argument("-b", help="The broadcast port", default=666,action=PortAction, type = int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    BroadcastServer (args.i,args.b).start()
            