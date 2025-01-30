# server.py
import eventlet
import socketio
from cryptography.fernet import Fernet

# Set up the server
sio = socketio.Server(cors_allowed_origins="*", async_mode="eventlet")
app = socketio.WSGIApp(sio)

# Generate an encryption key (for production, securely store this key)
AES_KEY = Fernet.generate_key()
cipher_suite = Fernet(AES_KEY)

rooms = {}

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")
    for room, users in rooms.items():
        if sid in users:
            users.remove(sid)
            break

@sio.event
def join(sid, data):
    username = data["username"]
    room = data["room"]
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(sid)
    sio.enter_room(sid, room)
    sio.emit("user_joined", {"username": username}, room=room)
    print(f"{username} joined room: {room}")

@sio.event
def send_message(sid, data):
    room = data["room"]
    message = data["message"]
    encrypted_message = cipher_suite.encrypt(message.encode()).decode()
    sio.emit("message", {"sid": sid, "message": encrypted_message}, room=room)

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
