import streamlit as st
import socketio
from cryptography.fernet import Fernet

# Generate AES key for encryption
AES_KEY = Fernet.generate_key()
cipher_suite = Fernet(AES_KEY)

# SocketIO client setup
sio = socketio.Client()

# Connect to the server
try:
    sio.connect("http://localhost:5000")
except socketio.exceptions.ConnectionError as e:
    st.error(f"Connection failed: {e}")

# Streamlit app state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "room" not in st.session_state:
    st.session_state["room"] = ""

# Function to encrypt messages
def encrypt_message(key, message):
    return cipher_suite.encrypt(message.encode()).decode()

# Function to decrypt messages
def decrypt_message(key, message):
    return cipher_suite.decrypt(message.encode()).decode()

# Handlers for SocketIO events
@sio.on("message")
def handle_message(data):
    decrypted_message = decrypt_message(AES_KEY, data["message"])
    st.session_state["messages"].append({"sender": data["sender"], "message": decrypted_message})
    st.experimental_rerun()

# Streamlit UI
st.title("Encrypted Chat App")

username = st.text_input("Enter your username:", key="username")
room_name = st.text_input("Enter room name:", key="room_name")

if st.button("Join Room"):
    if username and room_name:
        st.session_state["room"] = room_name
        sio.emit("join", {"username": username, "room": room_name})
    else:
        st.error("Both username and room name are required!")

# Message input and send button
if st.session_state["room"]:
    st.write(f"Connected to room: {st.session_state['room']}")
    message = st.text_input("Enter your message:", key="message_input")
    if st.button("Send Message"):
        if message:
            encrypted_message = encrypt_message(AES_KEY, message)
            sio.emit("message", {"room": st.session_state["room"], "sender": username, "message": encrypted_message})
            st.session_state["messages"].append({"sender": username, "message": message})  # Append unencrypted for local display
        else:
            st.error("Message cannot be empty!")

# Display chat messages
st.write("Chat Messages:")
for msg in st.session_state["messages"]:
    st.write(f"{msg['sender']}: {msg['message']}")
