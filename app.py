from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management

# Define the Clinic class with database interactions
class Clinic:
    def __init__(self, db_file):
        # Initialize database connection
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        # Create necessary tables if they don't exist
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS patients (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL UNIQUE,
                            phone TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS appointments (
                            id INTEGER PRIMARY KEY,
                            patient_id INTEGER,
                            service TEXT NOT NULL,
                            datetime TEXT NOT NULL,
                            FOREIGN KEY (patient_id) REFERENCES patients(id)
                        )''')
        self.conn.commit()

    def register_user(self, username, password):
        # Register a new user if username does not exist
        if not self.check_user_existence(username):
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return cursor.lastrowid
        return None

    def check_user_existence(self, username):
        # Check if a username already exists in the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        return cursor.fetchone() is not None

    def login_user(self, username, password):
        # Validate user login with username and password
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        return user[0] if user else None

    def get_user_profile(self, user_id):
        # Retrieve profile information for a logged-in user
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE user_id=?", (user_id,))
        return cursor.fetchone()

    def update_user_profile(self, user_id, name, email, phone):
        # Update profile information for the user
        cursor = self.conn.cursor()
        cursor.execute("UPDATE patients SET name=?, email=?, phone=? WHERE user_id=?", (name, email, phone, user_id))
        self.conn.commit()

    def schedule_appointment(self, patient_id, service, datetime):
        # Schedule a new appointment for the user
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO appointments (patient_id, service, datetime) VALUES (?, ?, ?)", (patient_id, service, datetime))
        self.conn.commit()
        return True, "Appointment scheduled successfully."

# Initialize the Clinic object with the database file
clinic = Clinic('clinic.db')

@app.route('/')
def index():
    # Home page route
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # User registration page and functionality
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = clinic.register_user(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Username already exists. Please choose a different username.")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # User login page and functionality
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = clinic.login_user(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Logout functionality to clear the session
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # User profile page and update functionality
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        clinic.update_user_profile(user_id, name, email, phone)
        return redirect(url_for('schedule'))
    profile_data = clinic.get_user_profile(user_id)
    return render_template('profile.html', profile_data=profile_data)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    # Appointment scheduling page
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        service = request.form['service']
        datetime = request.form['datetime']
        patient_id = session['user_id']  # Using session['user_id'] directly as patient_id
        success, message = clinic.schedule_appointment(patient_id, service, datetime)
        return render_template('result.html', success=success, message=message)
    return render_template('schedule.html')



if __name__ == '__main__':
    app.run(debug=True)
