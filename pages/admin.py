import streamlit as st
import os
from database import Database
from vector_store import VectorStore

def save_uploaded_file(uploaded_file):
    """Save uploaded file to uploads directory"""
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def main():
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Please login first")
        st.stop()
    
    if not st.session_state.user['is_admin']:
        st.error("Access denied. Admin privileges required.")
        st.stop()
    
    st.title("Admin Document Management")
    
    db = Database()
    current_doc = db.get_active_document()
    
    if current_doc:
        st.info(f"Current active document: {current_doc['filename']}")
    
    uploaded_file = st.file_uploader("Upload New Document", type=['txt', 'pdf'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            file_path = save_uploaded_file(uploaded_file)
            VectorStore.process_document(file_path)
            db.save_processed_document(uploaded_file.name, file_path)
            st.success(f"Document {uploaded_file.name} processed successfully!")

if __name__ == "__main__":
    main()