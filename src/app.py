from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
import streamlit as st

def init_database(user: str, password: str, host: str,
                  port: str, database: str) -> SQLDatabase:
    """
    Initialize a SQLDatabase object using the given connection details.

    Args:
        user (str): The username to use for the database connection.
        password (str): The password to use for the database connection.
        host (str): The hostname or IP address of the database server.
        port (str): The port number to use for the database connection.
        database (str): The name of the database to connect to.

    Returns:
        SQLDatabase: A SQLDatabase object representing the database connection.
    """
    # Construct URI for database connection using mysql-connector-python package's syntax
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

    # Create SQLDatabase object from URI.
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's SQL database.
    Based on the table schema below, write a SQL query that will answer the user's question. Take the conversation history into account.
    <SCHEMA>
    {schema}
    </SCHEMA>
    Conversation history:{chat_history}

    Write only the SQL query and nothing else. Do not write any other text or apply formatting.

    For example: 
    Question: Name 10 artists
    SQL Query: SELECT name FROM artists LIMIT 10;

    Now it's your turn to answer:

    Question: {question}
    SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model='gpt-3.5-turbo-0125')



def get_schema():
    return db.get_table_info()



if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        AIMessage(content="Hello, I am a MySQL assistant. Ask me anything about your database."),



    ]

st.set_page_config(page_title='Chat with MySQL', page_icon=':speech_balloon:')
st.title("Chat with MySQL")

with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using to MySQL. Connect to the database and start chatting.")

    # key parameter saves the value to a session state
    st.text_input("Host", value="localhost", key="host")
    st.text_input("Port", value="3306", key="port")
    st.text_input("User", value="root", key="user")
    st.text_input("Password", type="password", value="admin", key="password")
    st.text_input("Database", value="MyDatabase", key="db_name")

    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                user = st.session_state["user"],
                password = st.session_state["password"],
                host = st.session_state["host"],
                port = st.session_state["port"],
                database = st.session_state["db_name"],
            )
            st.session_state["db_connection"] = db
            st.success("Connected to database!")


# Display chat history and user input
for message in st.session_state["chat_history"]:
    if isinstance(message, AIMessage):
        with st.chat_message("ai"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query and user_query.strip() != "":
    
    st.session_state["chat_history"].append(HumanMessage(content=user_query))

    with st.chat_message("human"):
        st.markdown(user_query)

    with st.chat_message("ai"):
        response = "I don't know how to respond to that yet, sorry!"
        st.markdown(response)

    st.session_state["chat_history"].append(AIMessage(content=response))
    