import signal
import socket
import threading
import pickle
import sys
from random import choice
from string import ascii_uppercase

'''
So far server works as long as all devices are within same wifi. Global version coming soon.
General TODO:   
    - more civilised way to quit server than sending SIGINT xD
    - gui
In progress:
    - TOKENS FOR DIFFERENT TEAMS XDDDD Totally forgot. Server will generate token for each team. To join the team client
    must send INIT message with team's token (previously obtained from game supervisor, who also host the server) 
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
    clients = []  # connected clients TODO: (or not) define maximum number of clients (to be determined after testing)
    clients_data = []  # list of tuples: (connection (IP), name, lon, lat)
    tokens = []
    client_locations = {}

    def __init__(self):
        print("[STARTING] server is starting...")
        self.exit_request_flag = threading.Event()
        signal.signal(signal.SIGINT, self._sigint_handler)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created successfully")

    def _sigint_handler(self, signum, stack_frame):
        self.stop_server()

    # server abort
    def stop_server(self):
        for client in self.clients:
            if client:
                client[0].close()
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
        handle_new_connections_thread = threading.Thread(target=self._handle_new_connections)
        handle_new_connections_thread.daemon = True
        handle_new_connections_thread.start()
        # self._handle_new_connections()

    #  handle connected client
    def _handle_client(self, connection, address):
        print(f"[NEW CONNECTION] {address} connected")
        connected = True
        lock = threading.RLock()

        while connected:
            msg_length = connection.recv(HEADER_SIZE).decode(FORMAT)

            if msg_length:
                msg_length = int(msg_length)
                msg = pickle.loads(connection.recv(msg_length))
                reply = "Message received!"  # TODO: remove in final version (debug purposes only)

                if msg[0] == DISCONNECT_MESSAGE:
                    connected = False
                elif msg[0] == UPDATE_LOCATION:
                    with lock:
                        self.client_locations[(msg[1][0], connection)] = msg[1][1]
                elif msg[0] == REQUEST_LOCATIONS:
                    with lock:
                        locations = []
                        for key in self.client_locations.keys():
                            if key[0] == msg[1]:
                                locations.append(self.client_locations[key])
                        reply = locations
                elif msg[0] == INIT_MESSAGE:
                    token, name = msg[1].split(':', 1)
                    with lock:
                        if token in self.tokens:
                            self.client_locations.update({(token, connection): (name, -1, -1)})
                        else:
                            print("Incorrect token")

                print(f"[{address}] {msg}")
                self._send_message(connection, reply)

        with lock:
            self.clients.remove((connection, address))
        connection.close()

    # def _read_message(self, msg):
    #     lock = threading.RLock()
    #     reply = "Message received!"
    #     if msg == DISCONNECT_MESSAGE:
    #         connected = False
    #     elif isinstance(msg, tuple):
    #         with lock:
    #             tmp = (connection, msg[0], msg[1], msg[2])
    #             if tmp not in self.clients_data:
    #                 self.clients_data.append(tmp)
    #             # update client's location
    #             self.clients_data = [msg if data[0] == msg[0] else data for data in self.clients_data]
    #     elif msg == REQUEST_LOCATIONS:
    #         with lock:
    #             data = self.clients_data[:]
    #         reply = [(tup[1], tup[2], tup[3]) for tup in data]
    #     print(f"[{address}] {msg}")
    #     self._send_message(connection, reply)

    # send message to client
    def _send_message(self, connection, msg):
        msg = pickle.dumps(msg)
        length = len(msg)
        msg_length = str(length).encode(FORMAT)
        msg_length += b' ' * (HEADER_SIZE - len(msg_length))
        connection.send(msg_length)  # first sending length \
        connection.send(msg)         # then actual message

    # listen and connect new clients
    def _handle_new_connections(self):
        while True:
            connection, address = self.server.accept()
            self.clients.append((connection, address))
            handle_new_client_thread = threading.Thread(target=self._handle_client, args=(connection, address))
            try:
                handle_new_client_thread.daemon = True  # all spawned threads exist as long as the main thread does
                handle_new_client_thread.start()  # handle communication with each client in a separate thread
            except (KeyboardInterrupt, SystemExit, signal.SIGINT):
                self.stop_server()

            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}\n")

    def generate_token(self):
        # token = ''.join(choice(ascii_uppercase) for i in range(12))
        #
        # while token in self.tokens:
        #     token = ''.join(choice(ascii_uppercase) for i in range(12))

        token = "#ABCD"
        self.tokens.append(token)
        print(f"[NEW TOKEN] {token}")


# hardcoded testing
s = Server()
s.generate_token()
# s.generate_token()
# s.generate_token()
s.start()
input("Press enter to exit")
