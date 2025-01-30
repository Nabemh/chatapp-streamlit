import streamlit as st
import socketio
from cryptography.fernet import Fernet

# The key should be the same on both server and client
AES_KEY = b'YOUR_AES_KEY_HERE'  # Replace this with a shared key
cipher_suite = Fernet(AES_KEY)

sio = socketio.Client()

st.title("Streamlit Chat App")

# Initialize session state for room and messages
if "room" not in st.session_state:
    st.session_state["room"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def connect_to_server():
    try:
        sio.connect("http://localhost:5000")  # Connect to the server
        st.success("Connected to the server")
    except Exception as e:
        st.error(f"Connection failed: {e}")

@sio.on('message')
def handle_message(data):
    """Handle incoming messages from the server."""
    try:
        decrypted_message = cipher_suite.decrypt(data["message"].encode()).decode()
        # Append the message with username to session state for display
        st.session_state.messages.append(f"{data['username']}: {decrypted_message}")
    except Exception as e:
        st.session_state.messages.append(f"Error decrypting message: {e}")

@sio.on('error')
def handle_error(data):
    """Handle any errors."""
    st.error(f"Server error: {data['error']}")

def send_message():
    """Send a message to the server."""
    if st.session_state["room"]:
        message = st.text_input("Enter your message")
        if st.button("Send"):
            # Encrypt the message before sending
            encrypted_message = cipher_suite.encrypt(message.encode()).decode()
            sio.emit("message", {"username": username, "room": st.session_state["room"], "message": encrypted_message})

# Sidebar for user input (username and room)
with st.sidebar:
    username = st.text_input("Enter your username", value="User")
    room = st.text_input("Enter room name", value="")
    
    # Join room
    if st.button("Join Room"):
        if room:
            st.session_state["room"] = room
            connect_to_server()
            sio.emit("join", {"username": username, "room": room})
    
    # Leave room
    if st.button("Leave Room"):
        if st.session_state["room"]:
            sio.emit("leave", {"username": username, "room": st.session_state["room"]})
            st.session_state["room"] = ""

# Display messages from session state
if st.session_state["room"]:
    send_message()

# Display messages on the chat UI
st.subheader("Chat Messages")
for msg in st.session_state["messages"]:
    if msg.startswith(f"{username}:"):
        st.markdown(f"<p style='text-align:right;color:blue;'>{msg}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p>{msg}</p>", unsafe_allow_html=True)
