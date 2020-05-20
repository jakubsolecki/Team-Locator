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
    - improve handling messages
    - improve sending messages
    - clean code
'''

# TODO: set self._token after confirmation from server -> returns ERROR message that sets token to None again

# TODO: Store all tokens if admin -> done. Needs testing


# ============== Client is a singleton therefore it must always be created/accessed using get_instance() ==============
class Client:
    HEADER_SIZE = 64
    PORT = 5050
    # SERVER = socket.gethostbyname(socket.gethostname())
    SERVER = '142.93.227.45'
    ADDRESS = (SERVER, PORT)
    FORMAT = 'utf-8'
    INIT_MESSAGE = "!INIT"
    DISCONNECT_MESSAGE = "!DISCONNECT"
    REQUEST_LOCATIONS = "!REQUEST_LOCATIONS"
    UPDATE_LOCATION = "!UPDATE_LOCATION"
    ADMIN_TOKEN = "/0000000/"
    ADMIN_SETUP = "!ADMIN"
    ERROR = "!ERROR"
    CLOSE_GAME = "!CLOSE_GAME"
    START_GAME = "!START"

    # this key is secret, plz don't read it
    _KEY = b'epILh2fsAABQBJkwltgfz5Rvup3v9Hqkm1kNxtIu2xxYTalk1sWlIQs794Sf7PyBEE5WNI4msgxr3ArhbwSaTtfo9hevT8zkqxWd'

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
        self._my_socket = None
        self._server_ip = None
        self._token = None
        self._name = None
        self._connected = False
        self._initialised_flag = False
        self._sockets = []
        self._r_lock = threading.RLock()
        self._lon = 0
        self._lat = 0
        self._markers = []
        self._all_tokens = []

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
        sys.exit()

    # connect to server using it's ip <- will be provided form user input
    def connect(self, server_ip=SERVER):
        if not self._connected:
            try:
                with self._r_lock:
                    self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._my_socket.settimeout(20)
                    self._server_ip = server_ip
                    self._my_socket.connect((server_ip, self.PORT))
                    self._sockets.append(self._my_socket)
                    self._connected = True
                receive_messages_thread = threading.Thread(target=self._receive_message)
                receive_messages_thread.daemon = True
                receive_messages_thread.start()  # start listening to the server messages
            except OSError as errmsg:
                print(f"\n[ERROR] An error occurred while connecting to the server\n"
                      f" Error code: {errmsg.errno}\n"
                      f" Message: {errmsg.strerror}\n")

    def send_message(self, msg_type, msg):
        if msg_type == self.INIT_MESSAGE and self._connected:
            self._token, self._name = msg.split(':', 1)

        msg = (msg_type, msg)
        self._send_(msg)

    # requesting teammates' positions from server
    def _fetch_locations_from_server(self):
        while self._connected:
            self.send_message(self.REQUEST_LOCATIONS, self._token)
            time.sleep(5)

    # send current location to server every 10 seconds
    def _update_location(self):
        while self._connected:
            with self._r_lock:
                data_to_send = (self.UPDATE_LOCATION, (self._token, (self._name, self._lon, self._lat)))
            self._send_(data_to_send)
            time.sleep(10)

    # send message to the server
    def _send_(self, msg):
        if self._connected:
            msg = pickle.dumps(msg)
            digest = hmac.new(self._KEY, msg, hashlib.sha256).digest()
            length = len(digest) + len(msg) + 2
            header_length = str(length).encode(self.FORMAT)
            header_length += b' ' * (self.HEADER_SIZE - len(header_length))
            try:
                with self._r_lock:
                    self._my_socket.send(header_length)  # first sending length
                    self._my_socket.send(digest + b'  ' + msg)  # then actual message
            except OSError as errmsg:
                print(f"\n[ERROR] An error occurred while sending message\n"
                      f" Error code: {errmsg.errno}\n"
                      f" Message: {errmsg.strerror}\n")

    # listen to messages from the server
    def _receive_message(self):
        while self._connected:
            read_sockets, _, exception_sockets = select.select(self._sockets, [], self._sockets)
            for notified_socket in read_sockets:
                try:
                    header_length = notified_socket.recv(self.HEADER_SIZE).decode(self.FORMAT)

                    if header_length:
                        header_length = int(header_length)
                        header = notified_socket.recv(header_length)
                        digest, pickled_msg = header.split(b'  ')
                        check_digest = hmac.new(self._KEY, pickled_msg, hashlib.sha256).digest()
                        if hmac.compare_digest(check_digest, digest):
                            msg = pickle.loads(pickled_msg)
                        else:
                            print("[ERROR] Message denied due to digests incompatibility")
                            continue

                        # handling received messages according to their content
                        if msg[0] == self.REQUEST_LOCATIONS:
                            with self._r_lock:
                                self._markers = msg[1]

                        elif msg[0] == self.DISCONNECT_MESSAGE:
                            with self._r_lock:
                                self._connected = False
                                self._my_socket.shutdown(socket.SHUT_RDWR)
                                self._my_socket.close()
                            print("Closed connection with server")  # TODO: display
                            print(msg[1])

                        elif msg[0] == self.INIT_MESSAGE:
                            if msg[1] == "Setup complete":
                                update_location_thread = threading.Thread(target=self._update_location)
                                update_location_thread.daemon = True
                                update_location_thread.start()  # start updating current location
                                fetch_locations_thread = threading.Thread(target=self._fetch_locations_from_server)
                                fetch_locations_thread.daemon = True
                                fetch_locations_thread.start()
                            print("Registration complete")  # TODO: display

                        elif msg[0] == self.ERROR:
                            print(msg[1])  # TODO: display
                            if msg[1] == "Incorrect token":
                                with self._r_lock:
                                    self._token = None

                        elif msg[0] == self.ADMIN_SETUP:
                            self._all_tokens = msg[1][1]

                    else:
                        with self._r_lock:
                            print("\n[ERROR] Received empty msg. Closing socket...")
                            self._connected = False
                            self._my_socket.shutdown(socket.SHUT_RDWR)
                            self._my_socket.close()
                            self._my_socket = None
                        return None

                except OSError as errmsg:
                    print(f"\n[ERROR] An error occurred while reading message\n"
                          f" Error code: {errmsg.errno}\n"
                          f" Message: {errmsg.strerror}\n")


'''
if __name__ == "__main__":
    # hardcoded testing
    x = Client().get_instance()
    x.connect()
    input()
    x.send_message(x.INIT_MESSAGE, "#ABCD:Jakub Solecki")  # token:username
    #  for admin INIT message goes like "token:hostname:") after second : goes true for True and nothing for False
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



# hardcoded testing
x = Client().get_instance()
x.connect()
input()
x.send_message(x.INIT_MESSAGE, "#ABCD:Jakub Solecki")  # token:username     # JOINING SERVER
#x.send_message(x.INIT_MESSAGE, "#HARDCODEDTOKEN:Jakub Solecki")  # token:username     # HOSTING SERVER
#input()
#x.send_message("TEST", "Hello world!")
#input()
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

'''
