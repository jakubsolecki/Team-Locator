import socket
import threading
import pickle


HEADER_SIZE = 64
PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())  # If it is not used from localhost it can't be defined
ADDRESS = ('', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# TODO: objectify
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)


#  handle connected client
def handle_client(connection, address):
    print(f"[NEW CONNECTION] {address} connected")

    connected = True
    while connected:
        msg_length = connection.recv(HEADER_SIZE).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            # msg = connection.recv(msg_length).decode(FORMAT)
            msg = pickle.loads(connection.recv(msg_length))
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{address}] {msg}")
            # connection.send("Message received".encode(FORMAT))
            connection.send(pickle.dumps(msg))

    connection.close()


# handle new connections
def start():
    server.listen()
    # print(f"[LISTENING] Server is listening {SERVER}")
    while True:
        connection, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n")


print("[STARTING] server is starting...")
start()
