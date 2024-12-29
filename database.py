import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="docqa_db",
            user="docqa_admin",
            password="123WorK!@#",
            host="localhost"
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Chat history table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    uploaded_by INTEGER REFERENCES users(id),
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Add processed_documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS processed_documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(255) NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            self.conn.commit()

    def save_processed_document(self, filename, file_path):
        with self.conn.cursor() as cur:
            # Set all existing documents to inactive
            cur.execute("UPDATE processed_documents SET is_active = FALSE")
            # Add new document as active
            cur.execute(
                "INSERT INTO processed_documents (filename, file_path, is_active) VALUES (%s, %s, TRUE)",
                (filename, file_path)
            )
            self.conn.commit()

    def get_active_document(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM processed_documents WHERE is_active = TRUE")
            return cur.fetchone()

    def add_user(self, email, password_hash, is_admin=False):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash, is_admin) VALUES (%s, %s, %s) RETURNING id",
                (email, password_hash, is_admin)
            )
            self.conn.commit()
            return cur.fetchone()[0]
    
    def get_user(self, email):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cur.fetchone()
    
    def save_chat(self, user_id, message, response):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_history (user_id, message, response) VALUES (%s, %s, %s)",
                (user_id, message, response)
            )
            self.conn.commit()
    
    def get_chat_history(self, user_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM chat_history WHERE user_id = %s ORDER BY created_at",
                (user_id,)
            )
            return cur.fetchall()
    
    def save_document(self, filename, admin_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (filename, uploaded_by) VALUES (%s, %s) RETURNING id",
                (filename, admin_id)
            )
            self.conn.commit()
            return cur.fetchone()[0]
    
    def get_latest_document(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM documents ORDER BY uploaded_at DESC LIMIT 1"
            )
            return cur.fetchone()