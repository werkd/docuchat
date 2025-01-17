import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class VectorStore:
    VECTOR_STORE_PATH = "vectorstore/index"
    
    @staticmethod
    async def load_pdf(file_path):
        """Load text from a PDF file using PyPDFLoader"""
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        return "\n".join(pages)  # Combine text from all pages

    @staticmethod
    async def process_document(file_path):
        """Process a document and create vector embeddings"""
        if file_path.endswith('.pdf'):
            text = await VectorStore.load_pdf(file_path)  # Load PDF text
        else:
            loader = TextLoader(file_path)
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.split_documents(documents)
            text = "\n".join([doc.page_content for doc in docs])  # Combine text from documents

        # Continue with the existing processing logic
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(text)
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        # Save the vectorstore
        os.makedirs("vectorstore", exist_ok=True)
        vectorstore.save_local(VectorStore.VECTOR_STORE_PATH)
        
        return docs
    
    @classmethod
    def load(cls, allow_dangerous_deserialization=False):
        """Load the vector store if it exists"""
        if not os.path.exists(VectorStore.VECTOR_STORE_PATH):
            return None
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        return FAISS.load_local(VectorStore.VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=allow_dangerous_deserialization)