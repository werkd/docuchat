import os
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def load_vectorstore():
    try:
        # embeddings = OpenAIEmbeddings()
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vectorstore
    except Exception as e:
        st.error(f"No documents have been processed yet. Please contact admin." + str(e))
        return None


def main():
    st.title("Chat with Document")
    
    init_session_state()
    
    vectorstore = load_vectorstore()
    if not vectorstore:
        return
    
    # Initialize chat components
    llm = ChatOpenAI(temperature=0, api_key=openai_api_key, model='gpt-4o')
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectorstore.as_retriever(),
        return_source_documents=True
    )
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the documents"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            response = qa_chain({"question": prompt, "chat_history": st.session_state.chat_history})
            st.write(response["answer"])
            
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
            st.session_state.chat_history.append((prompt, response["answer"]))

if __name__ == "__main__":
    main()