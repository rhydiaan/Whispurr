# Importing relevent libraries
import websockets
import asyncio
import json
import copy

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

async def listener(websocket, path):
    '''
    Listens on any incoming message from client to the server.

    Parameters:
        websocket (object): The websocket connection to client.
        path: Required for connection using websockets but not used anywhere.
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


def disconnect(websocket: object):
    '''
    Once websocket is closed it disconnects the user

    Parameters:
        websocket (object): The websocket connection to client.
    '''
    for i in DB["users"]:
        for j in DB["users"][i]:
            if websocket == DB["users"][i][j]:
                DB["users"][i][j] = None
                print(f"User {DB['users'][i]} has disconnected.")
            else:
                print("Error disconnecting user.")


async def create_user(client_message: dict, websocket: object):
    '''
    Handles creating user.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (object): The websocket connection to client.
    '''
    new_user = copy.deepcopy(EMPTY_USER) # Creating a copy to make a unique user in the DB
    new_user["password"] = client_message["CreateUser"]["password"]
    new_user["websocket"] = websocket
    new_user["is_logged_in"] = True       
    DB["users"][client_message["CreateUser"]["id"]] = new_user
    await websocket.send("User created!")    
    return


async def login(client_message: dict, websocket: object):
    '''
    Handles user login.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (object): The websocket connection to client.
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


async def send_message(client_message: dict, websocket: object):
    '''
    Handles sending a message to another user.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (object): The websocket connection to client.
    '''
    client_message["SendMessage"]["target"] = client_message["SendMessage"]["target"].lower()
    client_message["id"] = client_message["id"].lower()
    if client_message["SendMessage"]["target"] not in DB["users"]:
        await websocket.send("User does not exist!")
        return


    if is_online(client_message["SendMessage"]["target"]): # If target websocket is currently connected then send message directly to that websocket 
        await DB["users"][client_message["SendMessage"]["target"]]["websocket"].send(client_message["SendMessage"]["message"]) # Send message to user specified
    else:
        DB["users"][client_message["SendMessage"]["target"].lower()]["messages"].append({
            "sender" : client_message["id"],
            "content" : client_message["SendMessage"]["message"]
        })


async def handle_message(client_message: dict, websocket: object):
    '''
    The main function that handles the message from the user.

    Parameters:
        client_message (dict): The message from the client to the server.
        websocket (object): The websocket connection to client.
    '''

    if "CreateUser" in client_message:
        client_message["CreateUser"]["id"] = client_message["CreateUser"]["id"].lower()
        if client_message["CreateUser"]["id"] in DB["users"]: # Checks if user exist already and exits if it does
            await websocket.send("User already exists please log in or choose another id")
            return 

        if "password" not in client_message["CreateUser"]: # Checks if there was a password specified.
            await websocket.send("Please choose a password.")
            return

        client_message["CreateUser"]["password"] = client_message["CreateUser"]["password"].lower()
        try: 
            await create_user(client_message, websocket)
        except Exception as e:
            print(f"Error handling create user, error : {e}")

    elif "Login" in client_message: # Handles the login request ensuring correct id and password
        await login(client_message, websocket)


    if DB["users"][client_message["id"].lower()]["is_logged_in"] == False:
        await websocket.send("Please login!")
        return


    if "SendMessage" in client_message:
        await send_message(client_message, websocket)

#########################################################################################################################
# Starting server
#########################################################################################################################
print(f"Started server. Listening on Port: {PORT}")
start_server = websockets.serve(listener, "localhost", PORT) 

asyncio.get_event_loop().run_until_complete(start_server) # Starting server
asyncio.get_event_loop().run_forever() # Ensure server runs indefinitely
