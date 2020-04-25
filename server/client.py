import socket
import pickle
import threading
import time


HEADER_SIZE = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # TODO: provide from user input
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDRESS)


# connect to server using it's ip <- will be provided form user input
def connect(server_ip):
    client.connect((server_ip, PORT))
    name = "Jan Kowalski"  # TODO: provide from user input
    # update_location_thread = threading.Thread(target=update_location, args=name)
    # update_location_thread.start()  # start updating current location
    receive_messages_thread = threading.Thread(target=receive)
    receive_messages_thread.start()  # start listening to the server messages


def update_location(name):
    while True:
        time.sleep(10)
        # TODO: reading location from gps
        lon = 51.6363
        lat = 51.6363
        data_to_send = pickle.dumps((name, lon, lat))
        send(data_to_send)


def send(msg):
    message = pickle.dumps(msg)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    client.send(send_length)
    client.send(message)
    # rep = pickle.loads(client.recv(2048))
    # print(rep)


def receive():
    while True:
        msg_length = client.recv(HEADER_SIZE).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = pickle.loads(client.recv(msg_length))
            print(msg)
            # if isinstance(msg, list):
            #     print(msg)
            #     #  update list of teammates locations
            # elif msg == "Message received":
            #     print(msg)


connect(SERVER)
send("Hello world!")
input()
send("Hello everyone!")
input()
send("Hello!")
input()
data = ("Jakub Solecki", 50.458673, 51.906735)
send(data)
input()
send(REQUEST_LOCATIONS)
input()
send(DISCONNECT_MESSAGE)
