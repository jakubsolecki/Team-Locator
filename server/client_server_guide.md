# Client-server overview

## General

### Message types and corresponding schemes 

Correct message is a two-element tuple: (msg_type, msg), where msg_type is a type of the message and msg is the actual 
message.

Supported message types:
  * "!INIT"
    - Should be first message send to the server. Registers client on the server.
    - Macro: INIT
    - Scheme: ("!INIT", "token:username")
    - Admin scheme: ("!INIT", "admin_token:hostname:") <- after second ':' goes 'True' or nothing. This is used as flag
      host's visibility to other players. 
    - Return message: ("!INIT", "Setup complete") or ("!ADMIN", "Setup complete") or 
      ("!ERROR", "Admin has been already set") or ("!ERROR", "Incorrect token")
      
  * "!DISCONNECT"
    - Used for intended and civilised disconnection. After receiving this message server and client will shutdown and
      close corresponding sockets.
    - Macro: DISCONNECT
    - Scheme: ("!DISCONNECT", token)
    - Return message: None
    
  * "!REQUEST_LOCATIONS"
    - Periodically send by client in order to fetch other teammates' locations from server.
    - Macro: REQUEST_LOCATIONS
    - Scheme: ("!REQUEST_LOCATIONS", token)
    - Return message: List of tuples (username, longitude, latitude)
    
  * "!UPDATE_LOCATION"
    - Periodically sent by client with actual coordinates.
    - Macro: UPDATE_LOCATION
    - Scheme: ("!UPDATE_LOCATION", (username, longitude, latitude))
    - Return message: None
    
  * "!REQUEST_TOKENS" (For admin only)
    - Send by admin with number of tokens that server will generate and send back.
    - Macro: REQUEST_TOKENS
    - Scheme: ("!REQUEST_TOKENS", number_of_tokens)
    - Return message: List of generated tokens.
    
  * "!ADMIN"
    - Send only as server's answer to successful admin registration.
    - Macro: ADMIN_SETUP
    - Scheme: ("!ADMIN", "Setup complete")
    - Return message: None
    
  * "!ERROR"
  - General purpose error informing.
  - Macro: ERROR
  - Scheme: ("!ERROR", msg), where msg should be string.
  - Return message: None
  
## Server

Server is build for hosting at most one game at the moment. It's main purpose is to send locations between members of 
same team. There cannot be more than 10 teams in one game.

### Tokens
Each team has its unique token. Tokens are generated for admin's request. Number of tokens sets number of teams. Each
token starts with a digit (0-9) that indicates team's number. The digit is followed by a fixed number of uppercase 
characters from the range of [A-Z]. The token must be specified in the INIT message
(see 'Message types and corresponding schemes' above), otherwise client won't be assigned to any team.

### A word about stored data
Server is not connected to any database. All stored data is considered to be volatile and is kept inside server's
class instance. During the game session server stores: 
  - __list of currently opened sockets__ - consists only of currently opened and valid sockets. When socket is closed - 
    upon receiving DISCONNECT message or after receiving empty message.
  - __dict of clients' data__ - dictionary with structure of {(token, client_socket): (name, longitude, latitude)}.
  - __Admin class__ - containing basic information about admin: socket (that is also in the list fo sockets), unique 
    admin's token and flag indicating whether admin's location si visible for everyone or not  
  - __list of tokens__
 
### Security
There's hardly any security on this server. The only implemented protection is signing pickle messages with hmac, so 
that ony trusted data is unpickled on both sides of the connection.  


## Client
Client is a class built-in an app. It manages all the communication with the server.
