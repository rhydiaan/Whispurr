# Importing relevent libraries
import websockets
import asyncio
import json

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

# DB["users"][client_message["SendMessage"]["target"]] = EMPTY_USER

print(f"Started server. Listening on Port: {PORT}")

async def listener(websocket, path):
    print("A client just connected")
    async for message in websocket:
        print(f"Received message from client: {message}")
        client_message = json.loads(message)
        await handle_message(client_message, websocket)

def is_online(target_id: str):
    return DB["users"][target_id]["websocket"] is not None


async def handle_message(client_message: dict, websocket: object):
    
    if "CreateUser" in client_message:
        client_message["CreateUser"]["id"] = client_message["CreateUser"]["id"].lower()
        if client_message["CreateUser"]["id"] in DB["users"]: # Checks if user exist already and exits if it does
            await websocket.send("User already exists please log in or choose another id")
            return 

        if "password" not in client_message["CreateUser"]: # Checks if there was a password specified.
            await websocket.send("Please choose a password.")
            return

        client_message["CreateUser"]["password"] = client_message["CreateUser"]["password"].lower()

        DB["users"][client_message["CreateUser"]["id"]] = EMPTY_USER 
        DB["users"][client_message["CreateUser"]["id"]]["password"] = client_message["CreateUser"]["password"]
        DB["users"][client_message["CreateUser"]["id"]]["websocket"] = websocket
        DB["users"][client_message["CreateUser"]["id"]]["is_logged_in"] = True
        await websocket.send("User created!")    
        return
    elif "Login" in client_message:
        client_message["Login"]["id"] = client_message["Login"]["id"].lower()
        client_message["Login"]["password"] = client_message["Login"]["password"].lower()
        if client_message["Login"]["id"] not in DB["users"]:
            await websocket.send("ID does not exist! Please create a user")
            return
        elif DB["users"][client_message["Login"]["id"]]["password"] == client_message["Login"]["password"]:
            DB["users"][client_message["Login"]["id"]]["websocket"] = websocket
            DB["users"][client_message["Login"]["id"]]["is_logged_in"] = True
            await websocket.send("Logged in!")    
            return
        else:
            await websocket.send("Wrong password!")

    if DB["users"][client_message["id"].lower()]["is_logged_in"] == False:
        await websocket.send("Please login!")
        return

    if "SendMessage" in client_message:
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

start_server = websockets.serve(listener, "localhost", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()