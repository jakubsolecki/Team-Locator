import socket
import pickle
import threading
import time
import sys

'''
General TODO:
    - setup messages:
        1) provide server ip from user input (glorious "connect" on app's main screen) by using connect(server_ip)
        2) provide token and username from user input (separate token for each team), then send it to the server in INIT 
        message (use send_message_via_client(msg, INIT_MESSAGE) with msg like "token:username"
    - reading current gps location (maybe providing it from outside -> change update_location(name))   
    - fetching data from server using button (use fetch_locations_from_server()) 
    - updating teammapview's list of teammates locations (in _receive_message() -> when message is a list)
    - allow changing names?
    - handling threads when closing app (mark as daemons?)
'''

# TODO: move to the class?
HEADER_SIZE = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # TODO: provide from user input (server IPv4 so far)
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
INIT_MESSAGE = "!INIT"
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"
UPDATE_LOCATION = "!UPDATE_LOCATION"


# ================== Client is a singleton so it must always be created/accessed using get_instance() ==================
class Client:
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
        self._token = None
        self._name = None
        self._connected_flag = False
        self._initialised_flag = False

    # connect to server using it's ip <- will be provided form user input
    def connect(self, server_ip):
        if not self._connected_flag:
            self._connected_flag = True
            self._client.connect((server_ip, PORT))
            # TODO: use in app
            # update_location_thread = threading.Thread(target=self._update_location)
            # update_location_thread.daemon = True  # needs testing in app
            # update_location_thread.start()  # start updating current location
            receive_messages_thread = threading.Thread(target=self._receive_message)
            # TODO: CHANGE DAEMONS TO CLEANING THREADS WHEN MAIN IS GOING TO EXIT
            receive_messages_thread.daemon = True  # needs testing in app
            receive_messages_thread.start()  # start listening to the server messages

    def send_message_via_client(self, msg, msg_type):
        if not self._initialised_flag and msg_type == INIT_MESSAGE:
            self._initialised_flag = True
            self._token, self._name = msg.split(':', 1)
        msg = (msg_type, msg)
        self._send_message(msg)

    # requesting teammates' positions from server
    def fetch_locations_from_server(self):
        self.send_message_via_client(self._token, REQUEST_LOCATIONS)

    # send current location to server every 10 seconds
    def _update_location(self):
        while True:
            time.sleep(10)
            # TODO: reading location from gps
            lon = 51.6363
            lat = 51.6363
            data_to_send = pickle.dumps((UPDATE_LOCATION, (self._token, (self._name, lon, lat))))
            self._send_message(data_to_send)

    # send message to the server
    def _send_message(self, msg):
        message = pickle.dumps(msg)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER_SIZE - len(send_length))
        self._client.send(send_length)  # first sending length
        self._client.send(message)  # then actual message

    # listen to messages from the server
    def _receive_message(self):
        while True:
            msg_length = self._client.recv(HEADER_SIZE).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = pickle.loads(self._client.recv(msg_length))

                # TODO: handling received messages according to their content
                if msg[0] == REQUEST_LOCATIONS:
                    #  update list of positions (just use received one)
                    pass
                elif msg[0] == DISCONNECT_MESSAGE:
                    self._connected_flag = False
                    print(msg[1])
                print(msg)


# hardcoded testing
x = Client().get_instance()
x.connect(SERVER)
x.send_message_via_client("#ABCD:Jakub Solecki", INIT_MESSAGE)  # token:username
input()
x.send_message_via_client("Hello world!", "TEST")
input()
x.send_message_via_client("#ABCD", REQUEST_LOCATIONS)
input()
data = ("Jakub Solecki", 50.458673, 51.906735)
x.send_message_via_client(("#ABCD", data), UPDATE_LOCATION)
input()
x.send_message_via_client("#ABCD", REQUEST_LOCATIONS)
input()
x.send_message_via_client("#ABCD", DISCONNECT_MESSAGE)
input("Press enter to exit")
sys.exit()
