import os
import logging
import streamlit as st
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from database import Database
from vector_store import VectorStore
from dotenv import load_dotenv
load_dotenv()

def main():
    logging.info('chat.py')
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Please login first")
        st.stop()

    st.title("Document QA")

    db = Database()
    active_doc = db.get_active_document()

    if not active_doc:
        st.error("No active document found. Please contact admin to upload a document.")
        st.stop()

    vectorstore = VectorStore.load(allow_dangerous_deserialization=True)
    if not vectorstore:
        st.error("Error loading document data. Please contact admin.")
        st.stop()

    st.info(f"Currently chatting with: {active_doc['filename']}")

    # Initialize chat components
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model='gpt-3.5-turbo', temperature=0)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectorstore.as_retriever(),
        return_source_documents=True
    )
    apikey = os.getenv("OPENAI_API_KEY")
    logging.info(apikey)

    # Initialize chat history if not exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the document"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            response = qa_chain({"question": prompt, "chat_history": []})
            st.write(response["answer"])
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

if __name__ == "__main__":
    main()
