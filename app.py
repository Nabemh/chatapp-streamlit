
# app.py
import streamlit as st
import socketio
from cryptography.fernet import Fernet

# Socket.IO client setup
sio = socketio.Client()
AES_KEY = Fernet.generate_key()
cipher_suite = Fernet(AES_KEY)

# Connect to the server
sio.connect("http://localhost:5000")

# Streamlit app state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "room" not in st.session_state:
    st.session_state["room"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = ""

def decrypt_message(message):
    try:
        return cipher_suite.decrypt(message.encode()).decode()
    except Exception as e:
        return "[Error decrypting message]"

def handle_message(data):
    sid = data["sid"]
    encrypted_message = data["message"]
    decrypted_message = decrypt_message(encrypted_message)
    if sid == sio.sid:
        st.session_state["messages"].append({"user": "You", "message": decrypted_message})
    else:
        st.session_state["messages"].append({"user": "Other", "message": decrypted_message})

sio.on("message", handle_message)

# Layout
st.title("Real-Time Chat App")

if "joined" not in st.session_state or not st.session_state["joined"]:
    st.session_state["joined"] = False
    with st.form("join_form"):
        st.session_state["username"] = st.text_input("Enter your username")
        st.session_state["room"] = st.text_input("Enter room name")
        if st.form_submit_button("Join"):
            sio.emit("join", {"username": st.session_state["username"], "room": st.session_state["room"]})
            st.session_state["joined"] = True
else:
    # Chat window
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["messages"]:
            if msg["user"] == "You":
                st.markdown(f"<div style='text-align: right;'><b>{msg['user']}:</b> {msg['message']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left;'><b>{msg['user']}:</b> {msg['message']}</div>", unsafe_allow_html=True)

    # Message input
    with st.form("send_form"):
        user_message = st.text_input("Type your message")
        if st.form_submit_button("Send"):
            if user_message.strip():
                sio.emit("send_message", {"room": st.session_state["room"], "message": user_message})
