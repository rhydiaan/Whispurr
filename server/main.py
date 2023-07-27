# Importing relevent libraries
from websockets.legacy.server import WebSocketServer as ws
import websockets
import asyncio
import json
import copy
import traceback

# Defining global variables

PORT = 11000
DB = {
    "users": {}
}

EMPTY_USER = {
    "websocket" : None,
    "messages" : [],
    "password" : "",
    "is_logged_in" : False
}


#########################################################################################################################
# Main server listener function
#########################################################################################################################

async def listener(websocket: ws, _):
    '''
    Listens on any incoming message from client to the server.

    Parameters:
        websocket (ws): The websocket connection to client.
    '''
    
    print("A client just connected")
    closed = asyncio.ensure_future(websocket.wait_closed())
    closed.add_done_callback(lambda task: disconnect(websocket)) # Runs cleanup function on websocket close
    async for message in websocket: # Handles each message
        print(f"Received message from client: {message}")
        client_message = json.loads(message)
        await handle_message(client_message, websocket) # Running main message handler function


#########################################################################################################################
# Message handler functions
#########################################################################################################################

def is_online(target_id: str):
    '''
    Checks if user is online.

    Parameters:
        target_id (str): The target user to check.
    Returns:
        bool: True if the user is connected.
    '''
    return DB["users"][target_id]["websocket"] is not None


def disconnect(websocket: ws):
    '''
    Once websocket is closed it disconnects the user

    Parameters:
        websocket (ws): The websocket connection to client.
    '''
    for user in DB["users"]:
        if websocket == DB["users"][user]["websocket"]:
            DB["users"][user]["is_logged_in"] == False
            DB["users"][user]["websocket"] = None
            print(f"User {DB['users'][user]} has disconnected.")


async def create_user(client_message: dict, websocket: ws):
    '''
    Handles creating user.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (ws): The websocket connection to client.
    '''
    client_message["CreateUser"]["id"] = client_message["CreateUser"]["id"].lower()
    if client_message["CreateUser"]["id"] in DB["users"]: # Checks if user exist already and exits if it does
        await websocket.send("User already exists please log in or choose another id")
        return 

    if "password" not in client_message["CreateUser"]: # Checks if there was a password specified.
        await websocket.send("Please choose a password.")
        return

    client_message["CreateUser"]["password"] = client_message["CreateUser"]["password"].lower()

    new_user = copy.deepcopy(EMPTY_USER) # Creating a copy to make a unique user in the DB
    new_user["password"] = client_message["CreateUser"]["password"]
    new_user["websocket"] = websocket
    new_user["is_logged_in"] = True       
    DB["users"][client_message["CreateUser"]["id"]] = new_user
    await websocket.send("User created!")  
    return


async def check_mailbox(client_message: dict, websocket: ws, instruction: str):
    '''
    Checks if ID received messages while offline and send them if they did.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (ws): The websocket connection to client.
        instruction (str): The instruction the message handler received.
    '''
    if not DB["users"][client_message[instruction]["id"]]["messages"]:
        return

    for message in DB["users"][client_message[instruction]["id"]]["messages"]:
        await websocket.send(message)


async def login(client_message: dict, websocket: ws):
    '''
    Handles user login.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (ws): The websocket connection to client.
    '''
    client_message["Login"]["id"] = client_message["Login"]["id"].lower()
    client_message["Login"]["password"] = client_message["Login"]["password"].lower()
    
    if client_message["Login"]["id"] not in DB["users"]: # Checks if a user exists then returns with a message to the client if it isn't in the DB
        await websocket.send("ID does not exist! Please create a user")
        return
    elif DB["users"][client_message["Login"]["id"]]["password"] == client_message["Login"]["password"]: # Checking for correct login credentials
        if DB["users"][client_message["Login"]["id"]]["websocket"] != None: # Checks if user is already logged in
            await websocket.send("User already logged in!")
            return
        
        DB["users"][client_message["Login"]["id"]]["websocket"] = websocket
        DB["users"][client_message["Login"]["id"]]["is_logged_in"] = True
        await websocket.send("Logged in!")   
        return
    else:
        await websocket.send("Wrong password!")


async def send_message(client_message: dict, websocket: ws):
    '''
    Handles sending a message to another user.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (ws): The websocket connection to client.
    '''
    client_message["SendMessage"]["target"] = client_message["SendMessage"]["target"].lower()
    client_message["id"] = client_message["id"].lower()
    if client_message["SendMessage"]["target"] not in DB["users"]:
        await websocket.send("User does not exist!")
        return

    message = {
        "message" : client_message["SendMessage"]["message"],
        "sender" : client_message["id"]
    }
    message_json = json.dumps(message) # Converting to json

    if is_online(client_message["SendMessage"]["target"]): # If target websocket is currently connected then send message directly to that websocket 
        await DB["users"][client_message["SendMessage"]["target"]]["websocket"].send(message_json) # Send message to user specified
    else:
        DB["users"][client_message["SendMessage"]["target"].lower()]["messages"].append(message_json)


async def handle_message(client_message: dict, websocket: ws):
    '''
    The main function that handles the message from the user.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (ws): The websocket connection to client.
    '''
    if "CreateUser" in client_message:
        try: 
            await create_user(client_message, websocket)
            await check_mailbox(client_message, websocket, "CreateUser") 
        except Exception as e:
            traceback.print_exc()
            print(f"Error handling create user, error : {e}")
        return

    elif "Login" in client_message: # Handles the login request ensuring correct id and password
        try:
            await login(client_message, websocket)
            await check_mailbox(client_message, websocket, "Login") 
        except Exception as e:
            traceback.print_exc()
            print(f"Error handling login user, error : {e}")
        return


    if DB["users"][client_message["id"].lower()]["is_logged_in"] == False:
        await websocket.send("Please login!")
        return


    if "SendMessage" in client_message:
        try:
            await send_message(client_message, websocket)
        except Exception as e:
            print(f"Error handling send message, error : {e}")

#########################################################################################################################
# Starting server
#########################################################################################################################

print(f"Started server. Listening on Port: {PORT}")
start_server = websockets.serve(listener, "localhost", PORT) 

asyncio.get_event_loop().run_until_complete(start_server) # Starting server
asyncio.get_event_loop().run_forever() # Ensure server runs indefinitely
