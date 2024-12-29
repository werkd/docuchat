import streamlit as st
import bcrypt
from database import Database

class Auth:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def signup(self, email, password, is_admin=False):
        if self.db.get_user(email):
            return False, "Email already exists"
        
        password_hash = self.hash_password(password)
        user_id = self.db.add_user(email, password_hash, is_admin)
        return True, user_id
    
    def login(self, email, password):
        user = self.db.get_user(email)
        if not user:
            return False, "User not found"
        
        if not self.verify_password(password, user['password_hash']):
            return False, "Invalid password"
        
        return True, user