# Importing relevent libraries
import websockets
import asyncio
import json

PORT = 11000
DB = {
    "users": {
       "user1" : {
            "websocket" : None,
            "messages" : [
                {
                    "sender" : "id",
                    "content" : "Hello"
                }
            ]
        }
    }
}

EMPTY_USER = {
    "websocket" : None,
    "messages" : []
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
    if "SendMessage" in client_message:
        if client_message["SendMessage"]["target"] not in DB["users"]:
            await websocket.send("User does not exist!")
            return

        if is_online(client_message["SendMessage"]["target"]): # If target websocket is currently connected then send message directly to that websocket 
            await DB["users"][client_message["SendMessage"]["target"]]["websocket"].send(client_message["SendMessage"]["message"]) # Send message to user specified
        else:
            DB["users"][client_message["SendMessage"]["target"]]["messages"].append({
                "sender" : client_message["SendMessage"]["sender"],
                "content" : client_message["SendMessage"]["message"]
            })
    elif "CreateUser" in client_message:
        if client_message["CreateUser"]["id"] not in DB["users"]:
            DB["users"][client_message["CreateUser"]["id"]] = EMPTY_USER
            DB["users"][client_message["CreateUser"]["id"]]["websocket"] = websocket
            await websocket.send("User created!")
    # elif "Connect" in client_message:
    #     if client_message["Connect"]["id"] not in DB["users"]:
    #         await websocket.send("ID does not exist! Please create a user")
    #         return
        
    #     if is_online(client_message["Connect"]["id"]):
    #         await websocket.send("Someone is already connected using that ID!")

start_server = websockets.serve(listener, "localhost", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()