import socket
import select
import pickle
import threading
import sys
import time
import signal
import hmac
import hashlib

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


# ============== Client is a singleton therefore it must always be created/accessed using get_instance() ==============
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
    REQUEST_TOKENS = "!REQUEST_TOKENS"
    ERROR = "!ERROR"
    # this key is secret, plz don't read it
    KEY = b'epILh2fsAABQBJkwltgfz5Rvup3v9Hqkm1kNxtIu2xxYTalk1sWlIQs794Sf7PyBEE5WNI4msgxr3ArhbwSaTtfo9hevT8zkqxWd'

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

        signal.signal(signal.SIGINT, self._sigint_handler)
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_ip = None
        self._token = None
        self._name = None
        self._connected = False
        self._initialised_flag = False
        self._sockets = []

    def _sigint_handler(self, signum, stack_frame):
        try:
            if self._connected:
                self.send_message(self.DISCONNECT_MESSAGE, self._token)
            self._my_socket.shutdown(socket.SHUT_RDWR)
            self._my_socket.close()
        except OSError as errmsg:
            print(f"\n[ERROR] An error occurred while handling SIGINT\n"
                  f" Error code: {errmsg.errno}\n"
                  f" Message: {errmsg.strerror}\n")
        sys.exit()  # TODO change in app

    # connect to server using it's ip <- will be provided form user input
    def connect(self, server_ip=SERVER):
        if not self._connected:
            try:
                self._server_ip = server_ip
                self._my_socket.connect((server_ip, self.PORT))
                self._my_socket.setblocking(False)
                self._sockets.append(self._my_socket)
                self._connected = True
                receive_messages_thread = threading.Thread(target=self._receive_message)
                receive_messages_thread.daemon = True
                receive_messages_thread.start()  # start listening to the server messages
                # update_location_thread = threading.Thread(target=self._update_location)
                # update_location_thread.daemon = True  # TODO: consider potential consequences on exit
                # update_location_thread.start()  # start updating current location
                # fetch_locations_thread = threading.Thread(target=self._fetch_locations_from_server)
                # fetch_locations_thread.daemon = True
                # fetch_locations_thread.start()
            except OSError as errmsg:
                print(f"\n[ERROR] An error occurred while connecting to the server\n"
                      f" Error code: {errmsg.errno}\n"
                      f" Message: {errmsg.strerror}\n")

    def send_message(self, msg_type, msg):
        if not self._initialised_flag and msg_type == self.INIT_MESSAGE and self._connected:
            self._initialised_flag = True
            self._token, self._name = msg.split(':', 1)
        msg = (msg_type, msg)
        self._send_(msg)

    # requesting teammates' positions from server
    def _fetch_locations_from_server(self):
        while self._connected:
            time.sleep(5)
            self.send_message(self.REQUEST_LOCATIONS, self._token)

    # send current location to server every 10 seconds
    def _update_location(self):
        while self._connected:
            time.sleep(10)
            # TODO: reading location from gps
            lon = 51.6363
            lat = 51.6363
            data_to_send = pickle.dumps((self.UPDATE_LOCATION, (self._token, (self._name, lon, lat))))
            self._send_(data_to_send)

    # send message to the server
    def _send_(self, msg):
        if self._connected:
            rLock = threading.RLock()
            msg = pickle.dumps(msg)
            digest = hmac.new(self.KEY, msg, hashlib.sha256).digest()
            length = len(digest) + len(msg) + 2
            header_length = str(length).encode(self.FORMAT)
            header_length += b' ' * (self.HEADER_SIZE - len(header_length))
            try:
                with rLock:
                    self._my_socket.send(header_length)  # first sending length
                    self._my_socket.send(digest + b'  ' + msg)  # then actual message
            except OSError as errmsg:
                print(f"\n[ERROR] An error occurred while sending message\n"
                      f" Error code: {errmsg.errno}\n"
                      f" Message: {errmsg.strerror}\n")

                # connected = False
                # self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # while not connected:
                #     try:
                #         self._my_socket.connect((self._server_ip, self.PORT))
                #         connected = True
                #         print("Reconnected successfully!")
                #     except OSError:
                #         time.sleep(2)

    # listen to messages from the server
    def _receive_message(self):
        rLock = threading.RLock()
        while self._connected:
            read_sockets, _, exception_sockets = select.select(self._sockets, [], self._sockets)
            for notified_socket in read_sockets:
                try:
                    header_length = notified_socket.recv(self.HEADER_SIZE).decode(self.FORMAT)
                    if header_length:
                        header_length = int(header_length)
                        header = notified_socket.recv(header_length)
                        digest, pickled_msg = header.split(b'  ')
                        check_digest = hmac.new(self.KEY, pickled_msg, hashlib.sha256).digest()
                        if hmac.compare_digest(check_digest, digest):
                            msg = pickle.loads(pickled_msg)
                        else:
                            print("[ERROR] Message denied due to digests incompatibility")
                            continue

                        # TODO: handling received messages according to their content
                        if msg[0] == self.REQUEST_LOCATIONS:
                            with rLock:
                                #  update list of positions
                                pass
                        elif msg[0] == self.DISCONNECT_MESSAGE:
                            with rLock:
                                self._connected = False
                                self._my_socket.shutdown(socket.SHUT_RDWR)
                                self._my_socket.close()
                            # self._my_socket = None
                            print(msg[1])
                        elif msg[0] == self.REQUEST_TOKENS:
                            pass
                        elif msg[0] == self.INIT_MESSAGE:
                            pass
                        elif msg[0] == self.ERROR:
                            pass

                        print(msg)

                except OSError as errmsg:
                    print(f"\n[ERROR] An error occurred while reading message\n"
                          f" Error code: {errmsg.errno}\n"
                          f" Message: {errmsg.strerror}\n")


# hardcoded testing
x = Client().get_instance()
x.connect()
input()
x.send_message(x.INIT_MESSAGE, "#ABCD:Jakub Solecki")  # token:username
input()
x.send_message("TEST", "Hello world!")
input()
x.send_message(x.REQUEST_LOCATIONS, "#ABCD")
input()
data = ("Jakub Solecki", 50.458673, 51.906735)
x.send_message(x.UPDATE_LOCATION, ("#ABCD", data))
input()
x.send_message(x.REQUEST_LOCATIONS, "#ABCD")
input()
x.send_message(x.DISCONNECT_MESSAGE, "#ABCD")
input("Press enter to exit")
sys.exit()
