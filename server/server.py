import signal
import socket
import pickle
import sys
import select
import hmac
import hashlib
import threading
from random import choice
from string import ascii_uppercase


class Server:
    HEADER_SIZE = 64
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())  # + ".local" so that it's no longer localhost-only
    ADDRESS = (SERVER, PORT)
    FORMAT = 'utf-8'
    INIT_MESSAGE = "!INIT"
    DISCONNECT_MESSAGE = "!DISCONNECT"
    REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"
    UPDATE_LOCATION = "!UPDATE_LOCATION"
    REQUEST_TOKENS = "!REQUEST_TOKENS"
    GAIN_ADMIN = "!ADMIN"
    ERROR = "!ERROR"
    # this key is secret, plz don't read it
    KEY = b'epILh2fsAABQBJkwltgfz5Rvup3v9Hqkm1kNxtIu2xxYTalk1sWlIQs794Sf7PyBEE5WNI4msgxr3ArhbwSaTtfo9hevT8zkqxWd'

    def __init__(self):
        print("[STARTING] server is starting...")
        signal.signal(signal.SIGINT, self._sigint_handler)
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sockets_list = [self._my_socket]  # storing active sockets
        self._clients = {}  # storing info about clients
        self._client_locations = {}  # storing clients' locations
        self._tokens = []  # storing all generated (per session) tokens
        self._admin_token = None  # special token reserved exclusively for an admin
        self._admin_socket = None
        print("Server socket created successfully")

    def _sigint_handler(self, signum, stack_frame):
        self.stop_server()

    # server abort
    def stop_server(self):
        print("\n[STOP] Server abort in progress...")
        self.close_game()
        sys.exit()

    # server start
    def start(self):
        try:
            self._my_socket.bind(self.ADDRESS)
        except OSError as errmsg:
            print(f"\n[ERROR] Binding failed. Error code: {errmsg.errno}\n"
                  f"Message:  {errmsg.strerror}\n"
                  f"Server start failed. Try again\n")
            # sys.exit()

        print("Socket binding complete")
        self._my_socket.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        self._admin_token = ''.join(choice(ascii_uppercase) for _ in range(5))
        print(f"[ADMINISTRATOR SETUP] Use this token to gain admin access: {self._admin_token}")
        self._listen_to_sockets()

    # cleaning after the game and getting ready for a new one
    def close_game(self):
        print("[CLEANING] Server is cleaning after the last game...")
        self._clients = {}
        self._tokens = []
        self._client_locations = {}
        for client_socket in self._sockets_list:
            if client_socket != self._my_socket:
                _ = self._send_message(client_socket, self.DISCONNECT_MESSAGE)
                try:
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                except OSError as errmsg:
                    print(f"\n[ERROR] An error occurred while closing socket {client_socket}\n"
                          f" Error code: {errmsg.errno}\n"
                          f" Message: {errmsg.strerror}\n")

        self._sockets_list = [self._my_socket]

    #  handle connected client
    def _handle_message(self, client_socket):
        try:
            header_length = client_socket.recv(self.HEADER_SIZE).decode(self.FORMAT)

            if header_length:
                header_length = int(header_length)
                header = client_socket.recv(header_length)
                digest, pickled_msg = header.split(b'  ')
                check_digest = hmac.new(self.KEY, pickled_msg, hashlib.sha256).digest()
                if hmac.compare_digest(check_digest, digest):
                    msg = pickle.loads(pickled_msg)
                else:
                    print("[ERROR] Message denied due to digests incompatibility")
                    return None

                print(f"[{self._clients[client_socket][0]}:{self._clients[client_socket][1]}] {msg}")

                if msg[0] == self.DISCONNECT_MESSAGE:  # disconnect current client
                    self._client_locations.pop((msg[1], client_socket))
                    print(f"Closing connection for {self._clients[client_socket][0]}:{self._clients[client_socket][1]}")
                    self._clients.pop(client_socket)
                    self._sockets_list.remove(client_socket)
                    client_socket.close()
                    return None
                elif msg[0] == self.UPDATE_LOCATION:  # update client's location
                    self._client_locations[(msg[1][0], client_socket)] = msg[1][1]
                    return None
                elif msg[0] == self.REQUEST_LOCATIONS:  # send client his teammates' locations
                    locations = []
                    for key in self._client_locations.keys():
                        if (key[0] == msg[1] or key[0] == self._admin_token) and key[1] != client_socket:
                            locations.append(self._client_locations[key])
                    self._send_message(client_socket, (self.REQUEST_LOCATIONS, locations))
                    return None
                elif msg[0] == self.INIT_MESSAGE:  # client setup
                    token, name = msg[1].split(':', 1)
                    if token in self._tokens:
                        self._client_locations.update({(token, client_socket): (name, -1, -1)})
                        self._send_message(client_socket, (self.INIT_MESSAGE, "Setup complete"))
                    elif token == self._admin_token:
                        self._client_locations.update({(token, client_socket): ("Host", -1, -1)})
                    else:
                        self._send_message(client_socket, (self.ERROR, "Incorrect token"))
                    return None
                elif msg[0] == self.REQUEST_TOKENS:  # generate and send tokens to admin
                    tokens_count = msg[1]
                    for i in range(tokens_count):
                        self.generate_token(7)
                    self._send_message(client_socket, (self.REQUEST_TOKENS, self._tokens))
                elif msg[0] == self.GAIN_ADMIN:
                    if self._admin_token is None:
                        self._send_message(client_socket, (self.GAIN_ADMIN, self._admin_token))
                    else:
                        self._send_message(client_socket, (self.GAIN_ADMIN, "Admin exists"))

                elif msg[0] == self.ERROR:
                    print(msg[1])
                else:
                    print("Unknown message type")
                    return None
            else:
                # TODO: change handling for not intended disconnection
                pass
                # print(f"Closing connection for {self._clients[client_socket][0]}:{self._clients[client_socket][1]}")
                # self._clients.pop(client_socket)
                # self._sockets_list.remove(client_socket)
                # client_socket.close()
        except OSError as errmsg:
            print(f"\n[ERROR] An error occurred while handling message from {client_socket}\n"
                  f" Error code: {errmsg.errno}\n"
                  f" Message: {errmsg.strerror}\n")

    # send message to client
    def _send_message(self, connection, msg):
        msg = pickle.dumps(msg)
        digest = hmac.new(self.KEY, msg, hashlib.sha256).digest()
        length = len(digest) + len(msg) + 2
        header_length = str(length).encode(self.FORMAT)
        header_length += b' ' * (self.HEADER_SIZE - len(header_length))
        try:
            connection.send(header_length)  # first sending length \
            connection.send(digest + b'  ' + msg)         # then actual message
        except OSError as errmsg:
            print(f"\n[ERROR] An error occurred while sending message to {connection}\n"
                  f" Error code: {errmsg.errno}\n"
                  f" Message: {errmsg.strerror}\n")
        return 1

    # accept new connections and append them to storage TODO: accept only trusted connections
    def _handle_new_connection(self):
        try:
            client_socket, client_address = self._my_socket.accept()
            self._sockets_list.append(client_socket)
            self._clients[client_socket] = client_address
            print(f"[NEW CONNECTION] Accepted new connection from {client_address}")
            print(f"[ACTIVE CONNECTIONS] {len(self._sockets_list) - 1}\n")
        except OSError as errmsg:
            print(f"\n[ERROR] An error occurred while accepting new connection\n"
                  f" Error code: {errmsg.errno}\n"
                  f" Message: {errmsg.strerror}\n")

    def _listen_to_sockets(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self._sockets_list, [], self._sockets_list)
            for notified_socket in read_sockets:
                if notified_socket == self._my_socket:
                    self._handle_new_connection()
                else:
                    self._handle_message(notified_socket)

    # generate new token for each team
    def generate_token(self, n):
        # token = ''.join(choice(ascii_uppercase) for i in range(n))
        #
        # while token in self.tokens:
        #     token = ''.join(choice(ascii_uppercase) for i in range(n))

        token = "#ABCD"
        self._tokens.append(token)
        print(f"[NEW TOKEN] {token}")


# hardcoded testing
s = Server()
s.generate_token(10)
# s.generate_token()
# s.generate_token()
s.start()
