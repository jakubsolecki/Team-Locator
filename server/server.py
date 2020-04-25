import socket
import threading
import pickle
import sys


HEADER_SIZE = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # + ".local" so that it's no longer localhost-only
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"

# TODO: wrap sends with try
# TODO: wrap everything in Server class

clients = []  # TODO: define maximum number of clients (needs thread testing)
clients_data = []  # list of tuples: (connection (IP), name, lon, lat)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket created successfully")
try:
    server.bind(ADDRESS)
except socket.error as errmsg:
    print("Bind failed. Error code: " + errmsg[0] + "\nMessage: " + errmsg[1])
    sys.exit()
print("Socket bind complete")


#  handle connected client
def handle_client(connection, address):
    print(f"[NEW CONNECTION] {address} connected")
    connected = True
    lock = threading.RLock()
    global clients_data

    while connected:
        msg_length = connection.recv(HEADER_SIZE).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = pickle.loads(connection.recv(msg_length))
            reply = "Message received!"  # TODO: remove in final version
            if msg == DISCONNECT_MESSAGE:
                connected = False
            elif isinstance(msg, tuple):
                with lock:
                    tmp = (connection, msg[0], msg[1], msg[2])
                    if tmp not in clients_data:
                        clients_data.append(tmp)
                    clients_data = [msg if data[0] == msg[0] else data for data in clients_data]  # update client location
            elif msg == REQUEST_LOCATIONS:
                with lock:
                    data = clients_data[:]
                reply = [(tup[1], tup[2], tup[3]) for tup in data]
            print(f"[{address}] {msg}")
            send(connection, reply)

    with lock:
        clients.remove((connection, address))
    connection.close()


# send message to client (connection)
def send(connection, msg):
    msg = pickle.dumps(msg)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    connection.send(send_length)
    connection.send(msg)


# listen and connect new clients
def handle_new_connections():
    while True:
        connection, address = server.accept()
        clients.append((connection, address))
        handle_new_client_thread = threading.Thread(target=handle_client, args=(connection, address))
        handle_new_client_thread.start()  # handle communication with each client in a separate thread
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n")


# prettier server stop (rather than ^C)
# def stop_server():
#     while True:
#         inpt = input()
#         if inpt == "QUIT":
#             if clients:
#                 for client in clients:
#                     connection = client[0]
#                     connection.close
#             sys.exit()


# server start
def start():
    server.listen()
    # thread = threading.Thread(target=stop_server)
    # thread.start()
    print(f"[LISTENING] Server is listening on {SERVER}")
    handle_new_connections()


print("[STARTING] server is starting...")
start()
