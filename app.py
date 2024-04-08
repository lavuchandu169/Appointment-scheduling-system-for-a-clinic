from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define the Clinic class and its functionalities
class Clinic:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Create tables for users, patients, and appointments
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,  -- Add user_id column
                            name TEXT NOT NULL,
                            email TEXT NOT NULL UNIQUE,
                            phone TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                            id INTEGER PRIMARY KEY,
                            patient_id INTEGER,
                            service TEXT NOT NULL,
                            datetime TEXT NOT NULL,
                            FOREIGN KEY (patient_id) REFERENCES patients(id)
                        )''')
        self.conn.commit()
