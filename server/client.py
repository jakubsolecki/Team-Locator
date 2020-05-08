import socket
import select
import pickle
import threading
import time
import sys
import errno
import time

'''
General TODO:
    - setup messages:
        1) provide server ip from user input (glorious "connect" on app's main screen) by using connect(server_ip)
        2) provide token and username from user input (separate token for each team), then send it to the server in INIT 
        message (use send_message_via_client(msg, INIT_MESSAGE) with msg like "token:username"
    - reading current gps location (maybe providing it from outside -> change update_location(name))
    - updating teammapview's list of teammates locations (in _receive_message() -> when message is a list)
    - allow changing names?
    - handling threads when closing app (mark as daemons?)
'''


# ================== Client is a singleton so it must always be created/accessed using get_instance() ==================
class Client:
    HEADER_SIZE = 64
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())  # TODO: provide from user input (server IPv4 so far)
    ADDRESS = (SERVER, PORT)
    FORMAT = 'utf-8'
    INIT_MESSAGE = "!INIT"
    DISCONNECT_MESSAGE = "!DISCONNECT"
    REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"
    UPDATE_LOCATION = "!UPDATE_LOCATION"
    ERROR = "!ERROR"
    __instance = None

    # singleton implementation
    @staticmethod
    def get_instance():
        if Client.__instance is None:
            Client()

        return Client.__instance

    def __init__(self):
        if Client.__instance is not None:  # singleton implementation
            raise Exception("Client class must be a singleton!")
        else:
            Client.__instance = self

        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_ip = None
        self._token = None
        self._name = None
        self._connected = False
        self._initialised_flag = False
        self._sockets = []

    # connect to server using it's ip <- will be provided form user input
    def connect(self, server_ip=SERVER):
        if not self._connected:
            self._server_ip = server_ip
            self._connected = True
            self._client.connect((server_ip, self.PORT))
            self._client.setblocking(False)
            self._sockets.append(self._client)
            # TODO: use in app
            # update_location_thread = threading.Thread(target=self._update_location)
            # update_location_thread.daemon = True  # TODO: consider potential consequences on exit
            # update_location_thread.start()  # start updating current location
            receive_messages_thread = threading.Thread(target=self._receive_message)
            receive_messages_thread.daemon = True  # TODO: consider potential consequences on exit
            receive_messages_thread.start()  # start listening to the server messages
            fetch_locations_thread = threading.Thread(target=self._fetch_locations_from_server())
            fetch_locations_thread.daemon = True
            fetch_locations_thread.start()

    def send_message(self, msg, msg_type):
        if not self._initialised_flag and msg_type == self.INIT_MESSAGE:
            self._initialised_flag = True
            self._token, self._name = msg.split(':', 1)
        msg = (msg_type, msg)
        self._send_(msg)

    # requesting teammates' positions from server
    def _fetch_locations_from_server(self):
        while True:
            time.sleep(5)
            self.send_message(self._token, self.REQUEST_LOCATIONS)

    # send current location to server every 10 seconds
    def _update_location(self):
        while True:
            time.sleep(10)
            # TODO: reading location from gps
            lon = 51.6363
            lat = 51.6363
            data_to_send = pickle.dumps((self.UPDATE_LOCATION, (self._token, (self._name, lon, lat))))
            self._send_(data_to_send)

    # send message to the server TODO: add RLock to avoid conflicts when handling exception
    def _send_(self, msg):
        message = pickle.dumps(msg)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER_SIZE - len(send_length))
        try:
            self._client.send(send_length)  # first sending length
            self._client.send(message)  # then actual message
        except OSError:
            self._connected = False  # TODO: local flag?
            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while not self._connected:
                try:
                    self._client.connect((self._server_ip, self.PORT))
                    self._connected = True
                    print("Reconnected successfully!")
                except OSError:
                    time.sleep(2)

    # listen to messages from the server
    def _receive_message(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self._sockets, [], self._sockets)
            for notified_socket in read_sockets:
                msg_length = notified_socket.recv(self.HEADER_SIZE).decode(self.FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = pickle.loads(notified_socket.recv(msg_length))

                    # TODO: handling received messages according to their content
                    if msg[0] == self.REQUEST_LOCATIONS:
                        #  update list of positions (with RLock I guess)
                        pass
                    elif msg[0] == self.DISCONNECT_MESSAGE:
                        self._connected = False
                        print(msg[1])
                    print(msg)


# hardcoded testing
x = Client().get_instance()
x.connect()
input()
x.send_message("#ABCD:Jakub Solecki", x.INIT_MESSAGE)  # token:username
input()
x.send_message("Hello world!", "TEST")
input()
x.send_message("#ABCD", x.REQUEST_LOCATIONS)
input()
data = ("Jakub Solecki", 50.458673, 51.906735)
x.send_message(("#ABCD", data), x.UPDATE_LOCATION)
input()
x.send_message("#ABCD", x.REQUEST_LOCATIONS)
input()
x.send_message("#ABCD", x.DISCONNECT_MESSAGE)
input("Press enter to exit")
sys.exit()
