import socket
import pickle
import threading
import time

'''
General TODO:
    - setup messages:
        1) provide server ip from user input (glorious "connect" on app's main screen)
        2) provide token from user input (separate token for each team), then send it to the server in INIT message
        3) provide name from user input (see above)
    - reading current gps location (maybe providing it from outside -> change update_location(name))     
    - updating teammapview's list of teammates locations (in receive() -> when message is a list)
'''

# TODO: move to the class?
HEADER_SIZE = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # TODO: provide from user input (server ipv4 so far)
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"


# ====================== Client is a singleton so it must always be created using get_instance() ======================
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
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server using it's ip <- will be provided form user input
    def connect(self, server_ip):
        self.client.connect((server_ip, PORT))
        name = "Jan Kowalski"  # TODO: provide from user input
        # update_location_thread = threading.Thread(target=update_location, args=name)
        # update_location_thread.start()  # start updating current location
        receive_messages_thread = threading.Thread(target=self.receive)
        receive_messages_thread.start()  # start listening to the server messages

    # send current location to server every 10 seconds
    def update_location(self, name):
        while True:
            time.sleep(10)
            # TODO: reading location from gps
            lon = 51.6363
            lat = 51.6363
            data_to_send = pickle.dumps((name, lon, lat))
            self.send(data_to_send)

    def send(self, msg):
        message = pickle.dumps(msg)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER_SIZE - len(send_length))
        self.client.send(send_length)  # first sending length
        self.client.send(message)  # then actual message

    def receive(self):
        while True:
            msg_length = self.client.recv(HEADER_SIZE).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = pickle.loads(self.client.recv(msg_length))
                print(msg)
                # TODO: handling received messages according to their content
                # if isinstance(msg, list):
                #    #  update list of teammates locations
                # elif msg == "Server aborted":
                #    #  notify user
                #  #  handling other messages


# hardcoded testing
x = Client().get_instance()
x.connect(SERVER)
x.send("Hello world!")
input()
x.send("Hello everyone!")
input()
x.send("Hello!")
input()
data = ("Jakub Solecki", 50.458673, 51.906735)
x.send(data)
input()
x.send(REQUEST_LOCATIONS)
input()
x.send(DISCONNECT_MESSAGE)
