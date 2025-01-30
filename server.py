from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable cross-origin requests for local testing

# Event when a client connects
@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit("message", {"sender": "Server", "message": "Welcome to the chat server!"})

# Event to handle joining a room
@socketio.on("join")
def handle_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    print(f"{username} joined room {room}")
    emit("message", {"sender": "Server", "message": f"{username} has joined the room."}, room=room)

# Event to handle leaving a room
@socketio.on("leave")
def handle_leave(data):
    username = data["username"]
    room = data["room"]
    leave_room(room)
    print(f"{username} left room {room}")
    emit("message", {"sender": "Server", "message": f"{username} has left the room."}, room=room)

# Event to handle chat messages
@socketio.on("message")
def handle_message(data):
    room = data["room"]
    print(f"Message from {data['sender']} in room {room}: {data['message']}")
    emit("message", data, room=room)

# Event when a client disconnects
@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
