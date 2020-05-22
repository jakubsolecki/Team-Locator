import signal
import socket
import pickle
import sys
import select
import hmac
import hashlib
from random import choice
from string import ascii_uppercase


class Admin:
    def __init__(self):
        self.token = None
        self.socket = None
        self.is_visible = False


# TODO: Read INIT message from admin (token:username:flag:number_of_tokens) -> crashes but it looks like it's an app bug
# TODO: add 'host-' before admin username -> done. Needs testing (can't be tested due to previous bug)

# TODO: better messaging when host closes game

class Server:
    HEADER_SIZE = 64
    PORT = 5050
    SERVER = ''
    ADDRESS = (SERVER, PORT)
    FORMAT = 'utf-8'
    INIT = "!INIT"
    DISCONNECT = "!DISCONNECT"
    REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"
    UPDATE_LOCATION = "!UPDATE_LOCATION"
    ERROR = "!ERROR"
    ADMIN_SETUP = "!ADMIN"
    ADMIN_TOKEN = "/0000000/"
    CLOSE_GAME = "!CLOSE_GAME"
    START_GAME = "!START"

    # this key is secret, plz don't read it
    _KEY = b'epILh2fsAABQBJkwltgfz5Rvup3v9Hqkm1kNxtIu2xxYTalk1sWlIQs794Sf7PyBEE5WNI4msgxr3ArhbwSaTtfo9hevT8zkqxWd'

    def __init__(self):
        print("[STARTING] server is starting...")
        signal.signal(signal.SIGINT, self._sigint_handler)
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sockets_list = [self._my_socket]  # storing active sockets
        self._clients = {}  # storing info about clients
        self._client_locations = {}  # storing clients' locations
        self._tokens = []  # storing all generated (per session) tokens
        self._admin = Admin()
        self._token_count = 0
        print("Server socket created successfully")

    def _sigint_handler(self, signum, stack_frame):
        self.stop_server()

    # server abort
    def stop_server(self):
        print("\n[STOP] Server abort in progress...")
        self.close_game()
        print("[EXIT] Server shutdown")
        sys.exit()

    # server start
    def start(self):
        try:
            self._my_socket.bind(self.ADDRESS)
        except OSError as errmsg:
            print(f"\n[ERROR] Binding failed. Error code: {errmsg.errno}\n"
                  f"Message:  {errmsg.strerror}\n"
                  f"Server start failed. Try again\n")

        print("Socket binding complete")
        self._my_socket.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        # self._admin.token = self.ADMIN_TOKEN
        print(f"[ADMINISTRATOR SETUP] Use this token to gain admin access: {self.ADMIN_TOKEN}")
        self._listen_to_sockets()

    # cleaning after the game and getting ready for a new one
    def close_game(self):
        print("[CLEANING] Server is cleaning after the last game...")
        self._clients = {}
        self._tokens = []
        self._client_locations = {}
        for client_socket in self._sockets_list:
            if client_socket != self._my_socket:
                _ = self._send_message(client_socket, self.DISCONNECT)
                try:
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                except OSError as errmsg:
                    print(f"\n[ERROR] An error occurred while closing socket {client_socket}\n"
                          f" Error code: {errmsg.errno}\n"
                          f" Message: {errmsg.strerror}\n")

        self._sockets_list = [self._my_socket]
        self._admin.socket = None
        self._admin.token = None
        self._admin.is_visible = False
        print("Game finished")

    #  handle connected client
    def _handle_message(self, client_socket):
        try:
            header_length = client_socket.recv(self.HEADER_SIZE).decode(self.FORMAT)

            if header_length:
                header_length = int(header_length)
                header = client_socket.recv(header_length)
                digest, pickled_msg = header.split(b'  ')
                check_digest = hmac.new(self._KEY, pickled_msg, hashlib.sha256).digest()
                if hmac.compare_digest(check_digest, digest):
                    msg = pickle.loads(pickled_msg)
                else:
                    print("[ERROR] Message denied due to digests incompatibility")
                    return None

                print(f"[{self._clients[client_socket][0]}:{self._clients[client_socket][1]}] {msg}")

                if msg[0] == self.DISCONNECT:  # disconnect current client and remove his data
                    if msg[1] in self._tokens and (msg[1], client_socket) in self._client_locations.keys():
                        self._client_locations.pop((msg[1], client_socket))
                    print(f"Closing connection for {self._clients[client_socket][0]}:{self._clients[client_socket][1]}")
                    self._clients.pop(client_socket)
                    if client_socket == self._admin.socket:
                        self._admin.socket = None
                        self._admin.token = None
                        self._admin.is_visible = False
                    self._sockets_list.remove(client_socket)
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    return None

                elif msg[0] == self.UPDATE_LOCATION:  # update client's location
                    self._client_locations[(msg[1][0], client_socket)] = msg[1][1]
                    return None

                elif msg[0] == self.REQUEST_LOCATIONS:  # send client his teammates' locations
                    if msg[1] == self.ADMIN_TOKEN:
                        locations = [value for key, value in self._client_locations.items() if key[1] != client_socket]
                    else:
                        locations = [value for key, value in self._client_locations.items() if
                                     (key[0] == msg[1] or (key[0] == self.ADMIN_TOKEN and self._admin.is_visible)) and
                                     key[1] != client_socket]
                    self._send_message(client_socket, (self.REQUEST_LOCATIONS, locations))
                    return None

                elif msg[0] == self.INIT:  # client setup
                    token, name = msg[1].split(':', 1)
                    if token in self._tokens:
                        self._client_locations.update({(token, client_socket): (name, 0, 0)})
                        self._send_message(client_socket, (self.INIT, "Setup complete"))
                        return None
                    elif token == self.ADMIN_TOKEN:
                        if self._admin.socket is None and ":" in name:  # and any(char.isdigit() for char in name):
                            self._admin.socket = client_socket
                            name, visibility, team_count = name.split(":", 2)
                            team_count = int(team_count)
                            self._admin.is_visible = bool(int(visibility))
                            self._client_locations.update({(token, client_socket): ('host- ' + name, 0, 0)})
                            self._send_message(client_socket, (self.INIT,
                                                               (self.ADMIN_SETUP,
                                                                self.generate_token(token_count=team_count))))
                            return None
                        else:
                            self._send_message(client_socket, (self.ERROR, "Admin has been already set"))
                    else:
                        self._send_message(client_socket, (self.ERROR, "Incorrect token"))
                    return None

                elif msg[0] == self.CLOSE_GAME and client_socket == self._admin.socket:
                    self.close_game()
                    return None

                elif msg[0] == self.ERROR:
                    print(msg[1])

                else:
                    print("Unknown message type")
                    return None
            else:
                print(f"Closing connection for {self._clients[client_socket][0]}:{self._clients[client_socket][1]}")
                self._clients.pop(client_socket)
                self._sockets_list.remove(client_socket)
                if self._admin.socket == client_socket:
                    self._admin.socket = None
                    self._admin.token = None
                    self._admin.is_visible = False
                key_to_remove = None
                for key in self._client_locations.keys():
                    if key[1] == client_socket:
                        key_to_remove = key
                        break
                if key_to_remove:
                    self._client_locations.pop(key_to_remove)
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()

        except OSError as errmsg:
            print(f"\n[ERROR] An error occurred while handling message from {client_socket}\n"
                  f" Error code: {errmsg.errno}\n"
                  f" Message: {errmsg.strerror}\n")

    # send message to client
    def _send_message(self, connection, msg):
        print(f"[MESSAGE] {msg}")
        msg = pickle.dumps(msg)
        digest = hmac.new(self._KEY, msg, hashlib.sha256).digest()
        length = len(digest) + len(msg) + 2
        header_length = str(length).encode(self.FORMAT)
        header_length += b' ' * (self.HEADER_SIZE - len(header_length))
        try:
            connection.send(header_length)          # first sending length \
            connection.send(digest + b'  ' + msg)   # then actual message
        except OSError as errmsg:
            print(f"\n[ERROR] An error occurred while sending message to {connection}\n"
                  f" Error code: {errmsg.errno}\n"
                  f" Message: {errmsg.strerror}\n")
        return 1

    # accept new connections and append them to storage
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
            read_sockets, _, exception_sockets = select.select(self._sockets_list, [], self._sockets_list, 600.0)
            for notified_socket in read_sockets:
                if notified_socket == self._my_socket:
                    self._handle_new_connection()
                else:
                    self._handle_message(notified_socket)

    # generate new token for each team
    def generate_token(self, token_count, token_len=7):
        if not self._tokens:
            for i in range(min(token_count, 10)):
                token = f'{i}' + ''.join(choice(ascii_uppercase) for _ in range(token_len))
                while token in self._tokens:
                    token = f'{i}' + ''.join(choice(ascii_uppercase) for _ in range(token_len))
                print(f"[NEW TOKEN] {token}")
                self._tokens.append(token)
        return self._tokens


if __name__ == "__main__":
    # hardcoded testing
    s = Server()
    # s.generate_token()
    # s.generate_token()
    s.start()
