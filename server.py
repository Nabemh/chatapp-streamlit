from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# The key should be the same as the client key
AES_KEY = b'YOUR_AES_KEY_HERE'  # Replace this with the same key
cipher_suite = Fernet(AES_KEY)

@app.route('/')
def index():
    return "Socket.IO server is running."

@socketio.on('join')
def on_join(data):
    """Handle a user joining the room."""
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'username': 'Server', 'message': f'{username} has joined the room.'}, to=room)

@socketio.on('message')
def handle_message(data):
    """Handle a user sending a message."""
    try:
        room = data['room']
        username = data['username']
        message = data['message']
        
        # Encrypt the message before broadcasting
        encrypted_message = cipher_suite.encrypt(message.encode()).decode()
        emit('message', {'username': username, 'message': encrypted_message}, to=room)
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('leave')
def on_leave(data):
    """Handle a user leaving the room."""
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'username': 'Server', 'message': f'{username} has left the room.'}, to=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
