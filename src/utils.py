
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.exc import ProgrammingError


def init_database(user: str, password: str, host: str,
                  port: str, database: str) -> SQLDatabase:
    # Construct URI for database connection using mysql-connector-python package's syntax
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

    # Create SQLDatabase object from URI.
    return SQLDatabase.from_uri(db_uri)


def get_sql_chain(db):
    """
    Returns a chain of runnables that generates a SQL query based on a user's question.

    The chain first generates the schema of the database, then prompts the user with a template
    that includes the schema and conversation history, and finally generates a SQL query using the
    OpenAI API. The final output of the chain is a string representing the SQL query.

    Parameters:
        db (SQLDatabase): A SQLDatabase object representing the database connection.

    Returns:
        Runnable: A chain of runnables that generates a SQL query.
    """
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

    Now, it's your turn to answer:

    Question: {question}
    SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model='gpt-3.5-turbo-0125')

    def get_schema(_):
        # Returns a string info about the tables in the db
        return db.get_table_info()

    return (
        # Assign the `schema` variable.
        RunnablePassthrough.assign(schema=get_schema)
        | prompt  # Prompt the user with the template.
        | llm     # Use the OpenAI API to generate a response.
        | StrOutputParser()  # Parse the response as a string.
    )


def get_response(user_query: str, db: SQLDatabase, chat_history: list) -> str:
    """
    Generates a natural language response to a user's SQL database question using a SQL chain and a language model.

    Args:
        user_query (str): The user's SQL database question.
        db (SQLDatabase): The SQLDatabase object representing the database connection.
        chat_history (list): A list of previous chat messages.

    Returns:
        str: The natural language response to the user's SQL database question or the SQL query if a ProgrammingError occurs.
    """
    sql_chain = get_sql_chain(db)

    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's SQL database.
    Based on the table schema, chat history, sql query, question, and reponse below, write a nature language response that will answer the user's question.

    <SCHEMA>
    {schema}
    </SCHEMA>

    Conversation history:{chat_history}
    SQL Query: <SQL>{query}</SQL>
    Question: {question}
    SQL Response: {response}    
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model='gpt-3.5-turbo-0125')

    chain = (
        RunnablePassthrough.assign(query=sql_chain)
        .assign(response=lambda vars: db.run(vars["query"]))
        .assign(schema=lambda _: db.get_table_info())
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        res = chain.invoke({
            "question": user_query,
            "chat_history": chat_history
        })
        return res
    except ProgrammingError as e:
        # Extract the query from the exception message
        error_message = str(e)
        start = error_message.find("SQL: ") + 5
        end = error_message.find("\n", start)
        query = error_message[start:end-1].strip()
        return query
