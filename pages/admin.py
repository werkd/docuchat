import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import pypdf

def init_session_state():
    if 'documents' not in st.session_state:
        st.session_state.documents = []

def save_uploaded_file(uploaded_file):
    with open(f"uploads/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    return f"uploads/{uploaded_file.name}"


def process_document(file_path):
    # Determine the file extension
    file_extension = file_path.split('.')[-1].lower()

    # Load documents based on file type
    if file_extension == 'txt':
        loader = TextLoader(file_path)
        documents = loader.load()  # Load documents for txt files
    elif file_extension == 'pdf':
        from langchain_community.document_loaders import PyPDFLoader  # Import PyPDFLoader
        loader = PyPDFLoader(
            file_path=file_path,
            password=None,  # Set password if needed
            extract_images=True
        )
        documents = loader.load()  # Load documents using PyPDFLoader
    elif file_extension == 'xlsx':
        from langchain_community.document_loaders import ExcelLoader  # Import ExcelLoader
        loader = ExcelLoader(file_path)  # Use ExcelLoader for .xlsx files
        documents = loader.load()  # Load documents for xlsx files
    else:
        st.error("Unsupported file type.")
        return []  # Return an empty list for unsupported file types

    # If using loader for txt or xlsx
    if file_extension in ['txt', 'xlsx']:
        try:
            documents = loader.load()
        except Exception as e:
            st.error(f"Error loading document: {e}")
            return []  # Return an empty list or handle as needed

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local("faiss_index")

    return docs


# def process_document(file_path):
#     loader = TextLoader(file_path)
#     try:
#         documents = loader.load()
#     except Exception as e:
#         st.error(f"Error loading document: {e}")
#         return []  # Return an empty list or `handle as needed
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     docs = text_splitter.split_documents(documents)
    
#     embeddings = OpenAIEmbeddings()
#     vectorstore = FAISS.from_documents(docs, embeddings)
#     vectorstore.save_local("faiss_index")
    
#     return docs

def main():
    st.title("Admin Document Management")
    
    if not st.session_state.get("authenticated", False):
        admin_password = st.text_input("Enter admin password", type="password")
        if admin_password == "password123":  # Replace with secure authentication
            st.session_state.authenticated = True
        else:
            st.warning("Please enter valid admin credentials")
            return
    
    init_session_state()
    
    uploaded_file = st.file_uploader("Upload Document", type=['txt', 'pdf'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            file_path = save_uploaded_file(uploaded_file)
            docs = process_document(file_path)
            st.session_state.documents.append({
                'name': uploaded_file.name,
                'path': file_path
            })
            st.success(f"Document {uploaded_file.name} processed successfully!")
    
    if st.session_state.documents:
        st.subheader("Processed Documents")
        for doc in st.session_state.documents:
            st.write(f"- {doc['name']}")

if __name__ == "__main__":
    main()
