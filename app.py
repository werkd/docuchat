import streamlit as st
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
import pandas as pd
import pathlib
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state for vector store
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None

def create_vector_db(file, db_name="local_vector_db"):
    """Create a vector database from an uploaded file"""
    
    # Create a temporary file to store the uploaded file
    temp_file_path = f"temp_{file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(file.getvalue())
    
    # Determine file type and use appropriate loader
    file_extension = pathlib.Path(file.name).suffix.lower()
    
    try:
        if file_extension == '.pdf':
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
        elif file_extension == '.txt':
            loader = TextLoader(temp_file_path)
            documents = loader.load()
        elif file_extension in ['.xlsx', '.csv']:
            if file_extension == '.xlsx':
                df = pd.read_excel(temp_file_path)
                temp_csv = 'temp.csv'
                df.to_csv(temp_csv, index=False)
                temp_file_path = temp_csv
            
            loader = CSVLoader(
                temp_file_path,
                csv_args={
                    'delimiter': ',',
                    'quotechar': '"',
                    'fieldnames': None
                }
            )
            documents = loader.load()

        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create and save the vector store
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(db_name)
        
        # Clean up temporary files
        os.remove(temp_file_path)
        if file_extension == '.xlsx' and os.path.exists('temp.csv'):
            os.remove('temp.csv')
            
        return vector_store
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def load_vector_db(db_name="local_vector_db"):
    """Load an existing vector database"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_store = FAISS.load_local(db_name, embeddings)
        return vector_store
    except Exception as e:
        st.warning("No existing vector database found. Please upload a document first.")
        return None

def query_document(query, vector_store):
    """Query the vector store and get response from LLM"""
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            st.error("OpenAI API key not found. Please check your .env file.")
            return None
            
        llm = OpenAI(temperature=0, api_key=openai_api_key)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3})
        )
        
        response = qa_chain.invoke(query)
        return response
    except Exception as e:
        st.error(f"Error querying document: {str(e)}")
        return None

# Streamlit UI
st.title("Document Q&A System")
st.write("Upload a document and ask questions about its content!")

# File upload section
st.subheader("1. Upload Document")
uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt', 'xlsx', 'csv'])

if uploaded_file is not None:
    if st.button("Process Document"):
        with st.spinner("Processing document..."):
            st.session_state.vector_store = create_vector_db(uploaded_file)
            if st.session_state.vector_store:
                st.success("Document processed successfully!")

# Query section
st.subheader("2. Ask Questions")
query = st.text_input("Enter your question:")

if query:
    if st.session_state.vector_store is None:
        try:
            st.session_state.vector_store = load_vector_db()
        except Exception as e:
            st.error("Please upload and process a document first.")

    if st.session_state.vector_store:
        with st.spinner("Finding answer..."):
            response = query_document(query, st.session_state.vector_store)
            if response:
                st.write("Answer:")
                st.write(response['result'])
