import signal
import socket
import pickle
import sys
import select
from random import choice
from string import ascii_uppercase

'''
So far server works as long as all devices are within same wifi. Global version coming soon.
General TODO:   
    - gui
    _ mapview for game supervisor (displaying ALL players)
'''

# TODO: move to the class?
HEADER_SIZE = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # + ".local" so that it's no longer localhost-only
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
INIT_MESSAGE = "!INIT"
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"
UPDATE_LOCATION = "!UPDATE_LOCATION"


class Server:

    def __init__(self):
        print("[STARTING] server is starting...")
        signal.signal(signal.SIGINT, self._sigint_handler)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets_list = [self.server]  # storing active sockets
        self.clients = {}  # storing info about clients
        self.client_locations = {}  # storing clients' locations
        self.tokens = []  # storing all generated (per session) tokens
        print("Server socket created successfully")

    def _sigint_handler(self, signum, stack_frame):
        self.stop_server()

    # server abort
    def stop_server(self):
        for client_socket in self.sockets_list:
            client_socket.close()
        self.server.close()
        sys.exit()

    # server start
    def start(self):
        try:
            self.server.bind(ADDRESS)
        except socket.error as errmsg:
            print("Bind failed. Error code: " + errmsg[0] + "\nMessage: " + errmsg[1])
            sys.exit()
        print("Socket bind complete")
        self.server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        self._listen_to_sockets()

    # stop server (close connections) but continue process
    def stop(self):
        pass

    #  handle connected client
    def _handle_message(self, client_socket):
        try:
            msg_length = client_socket.recv(HEADER_SIZE).decode(FORMAT)

            if msg_length:
                msg_length = int(msg_length)
                msg = pickle.loads(client_socket.recv(msg_length))
                reply = "Message received!"  # TODO: remove in final version (debug purposes only)

                if msg[0] == DISCONNECT_MESSAGE:  # disconnect current client
                    self.client_locations.pop((msg[1], client_socket))
                    self._send_message(client_socket, (DISCONNECT_MESSAGE, "Disconnected from the server"))
                    print(f"Closing connection for {self.clients[client_socket][0]}:{self.clients[client_socket][1]}")
                    self.clients.pop(client_socket)
                    self.sockets_list.remove(client_socket)
                    client_socket.close()
                elif msg[0] == UPDATE_LOCATION:  # message contains client's updated location
                    self.client_locations[(msg[1][0], client_socket)] = msg[1][1]
                elif msg[0] == REQUEST_LOCATIONS:  # client requested all teammates' locations
                    locations = []
                    for key in self.client_locations.keys():
                        if key[0] == msg[1]:  # fetch only clients with same token
                            locations.append(self.client_locations[key])
                    reply = (REQUEST_LOCATIONS, locations)
                elif msg[0] == INIT_MESSAGE:  # client setup
                    token, name = msg[1].split(':', 1)
                    if token in self.tokens:
                        self.client_locations.update({(token, client_socket): (name, -1, -1)})  # TODO: real coords
                    else:
                        print("Incorrect token")

                print(f"[{self.clients[client_socket][0]}:{self.clients[client_socket][1]}] {msg}")
                self._send_message(client_socket, reply)

            else:
                print(f"Closing connection for {self.clients[client_socket][0]}:{self.clients[client_socket][1]}")
                self.clients.pop(client_socket)
                self.sockets_list.remove(client_socket)
                client_socket.close()
        except:
            pass

    # send message to client
    def _send_message(self, connection, msg):
        msg = pickle.dumps(msg)
        length = len(msg)
        msg_length = str(length).encode(FORMAT)
        msg_length += b' ' * (HEADER_SIZE - len(msg_length))
        connection.send(msg_length)  # first sending length \
        connection.send(msg)         # then actual message

    # accept new connections and append them to storage
    def _handle_new_connection(self):
        client_socket, client_address = self.server.accept()
        self.sockets_list.append(client_socket)
        self.clients[client_socket] = client_address
        print(f"[NEW CONNECTION ]Accepted new connection from {client_address}")  # TODO: display better info
        print(f"[ACTIVE CONNECTIONS] {len(self.sockets_list) - 1}\n")

    def _listen_to_sockets(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
            for notified_socket in read_sockets:
                if notified_socket == self.server:
                    self._handle_new_connection()
                else:
                    self._handle_message(notified_socket)

    # generate new token for each team. Must be done before calling start()
    def generate_token(self):
        # token = ''.join(choice(ascii_uppercase) for i in range(10))
        #
        # while token in self.tokens:
        #     token = ''.join(choice(ascii_uppercase) for i in range(10))

        token = "#ABCD"
        self.tokens.append(token)
        print(f"[NEW TOKEN] {token}")


# hardcoded testing
s = Server()
s.generate_token()
# s.generate_token()
# s.generate_token()
s.start()
