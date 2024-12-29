import streamlit as st
from auth import Auth

st.set_page_config(
    page_title="Document Chat System",
    page_icon="📚"
)

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None

def main():
    init_session_state()
    auth = Auth()
    
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None

    st.title("Welcome to Document Chat System")
    
    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
        with tab1:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                success, result = auth.login(email, password)
                if success:
                    st.session_state.user = result
                    st.rerun()
                else:
                    st.error(result)
        
        with tab2:
            st.subheader("Sign Up")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            is_admin = st.checkbox("Sign up as admin")
            
            if st.button("Sign Up"):
                success, result = auth.signup(email, password, is_admin)
                if success:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error(result)
    
    else:
        st.write(f"Welcome, {st.session_state.user['email']}!")
        if st.session_state.user['is_admin']:
            st.write("You have admin privileges. Go to the Admin page to manage documents.")
        else:
            st.write("Go to the Chat page to start chatting with documents.")

        if st.button("Logout"):
            st.session_state.user = None
            print("Logged out. ")
            st.rerun()

        # if st.session_state.vector_store is None:
        #     try:
        #         st.session_state.vector_store = load_vector_db()
        #     except Exception as e:
        #         st.error("Please upload and process a document first.")

if __name__ == "__main__":
    main()