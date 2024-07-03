from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st

from utils import init_database, get_sql_chain, get_response


# Load environment variables from .env file
load_dotenv()

# Set page title and icon
st.set_page_config(page_title='Chat with MySQL', page_icon=':speech_balloon:')

# Set page title
st.title("Chat with MySQL")

# Flag for chat status
if "is_disabled" not in st.session_state:
    st.session_state["is_disabled"] = True

# Sidebar settings
with st.sidebar:
    st.subheader("Settings")  # Sidebar header
    # Sidebar text
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")

    # Input fields for database connection details
    st.text_input("Host", value="localhost", key="host")
    st.text_input("Port", value="3306", key="port")
    st.text_input("User", value="root", key="user")
    st.text_input("Password", type="password", value="admin", key="password")
    st.text_input("Database", value="world", key="db_name")

    # Connect button
    if st.button("Connect"):
        try:
            with st.spinner("Connecting to database..."):
                # Initialize database connection
                db = init_database(
                    user=st.session_state["user"],
                    password=st.session_state["password"],
                    host=st.session_state["host"],
                    port=st.session_state["port"],
                    database=st.session_state["db_name"],
                )

                # Store database connection in session state
                st.session_state["db_connection"] = db
                st.success("Connected to database!")  # Success message
                st.session_state["is_disabled"] = False
        except:
            st.error(
                "Failed to connect to database. Please check your connection details and try again.")

# Check if chat history exists in session state. If not, create a default greeting message.
if not st.session_state["is_disabled"]:
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            AIMessage(
                content="Hello, I am a MySQL assistant. Ask me anything about your database.")
        ]

    # Display chat history and user input
    for message in st.session_state["chat_history"]:
        if isinstance(message, AIMessage):
            # Display AI message
            with st.chat_message("ai"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            # Display human message
                with st.chat_message("human"):
                    st.markdown(message.content)

# Get user input
user_query = st.chat_input(
    "Type a message...", disabled=st.session_state["is_disabled"])

# If user input is not empty, process and store the input and the generated response
if user_query and user_query.strip() != "":
    st.session_state["chat_history"].append(
        HumanMessage(content=user_query))  # Store human message

    with st.chat_message("human"):
        st.markdown(user_query)  # Display human message

    with st.chat_message("ai"):
        sql_chain = get_sql_chain(
            st.session_state["db_connection"])  # Generate SQL query
        response = get_response(
            user_query, st.session_state["db_connection"], st.session_state["chat_history"])  # Generate response
        st.markdown(response)  # Display response

    st.session_state["chat_history"].append(
        AIMessage(content=response))  # Store AI message
