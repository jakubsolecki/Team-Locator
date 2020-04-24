import socket
import pickle


HEADER_SIZE = 64
PORT = 5050
SERVER = "127.0.1.1"  # different when the client doesn't run on the same machine (check eg. IP list on router )
ADDRESS = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)


def send(msg):
    # message = msg.encode(FORMAT)
    # msg_length = len(message)
    # send_length = str(msg_length).encode(FORMAT)
    # send_length += b' ' * (HEADER_SIZE - len(send_length))
    # client.send(send_length)
    # client.send(message)
    # print(client.recv(2048).decode(FORMAT))  # TODO: buffer data
    message = pickle.dumps(msg)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    client.send(send_length)
    client.send(message)
    # print(client.recv(2048).decode(FORMAT))
    print(pickle.loads(client.recv(1024)))


send("Hello world!")
input()
send("Hello everyone!")
input()
send("Hello!")
input()
data = {"ID": 1, "name": "Jakub Solecki", "lon": 50.458673, "lat": 51.906735}
# data_to_send = pickle.dumps(data)
send(data)
send(DISCONNECT_MESSAGE)
