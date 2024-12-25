import streamlit as st

st.set_page_config(
    page_title="Document Chat System",
    page_icon="📚"
)

st.title("Welcome to Document Chat System")

st.write("""
## Choose your role:

- **👤 Users**: Click on 'Chat' in the sidebar to start chatting with the documents
- **🔑 Admins**: Click on 'Admin' in the sidebar to manage documents

Please select your desired page from the sidebar.
""")