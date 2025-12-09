from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_change_this' # Required for session management
DATABASE = 'users.db'

# --- Database Functions ---

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Allows accessing rows by column name
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        # Create users table with a 'role' column for admin/normal user differentiation
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        db.commit()

def add_initial_admin():
    with app.app_context():
        db = get_db()
        cursor = db.execute("SELECT * FROM users WHERE username = 'ADMIN'")
        if not cursor.fetchone():
            # Hash the specified ADMIN password "Hex123abc45!"
            hashed_password = generate_password_hash("Hex123abc45!", method='pbkdf2:sha256')
            db.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ('ADMIN', hashed_password, 'admin'))
            db.commit()

# --- Routes ---

@app.route('/')
def index():
    # Redirect logged-in users to their respective pages
    if 'username' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('terminal_page'))
        else:
            return redirect(url_for('home'))
    return redirect(url_for('login_signup'))

@app.route('/login_signup', methods=['GET', 'POST'])
def login_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            # Check password hash if user exists
            if check_password_hash(user['password_hash'], password):
                session['username'] = user['username']
                session['role'] = user['role']
                if user['role'] == 'admin':
                    return redirect(url_for('terminal_page'))
                else:
                    return redirect(url_for('home'))
            else:
                flash('Invalid username or password')
        else:
            # Auto-signup if username doesn't exist
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            # New users default to 'normal' role
            db.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, hashed_password, 'normal'))
            db.commit()
            session['username'] = username
            session['role'] = 'normal'
            return redirect(url_for('home'))
        db.close()
    
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login_signup'))
    return render_template('home.html', username=session['username'])

@app.route('/terminal')
def terminal_page():
    if session.get('role') != 'admin':
        flash('Access Denied: Admin privileges required.')
        return redirect(url_for('home'))
    return render_template('terminal.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login_signup'))

# --- Terminal API Endpoint ---

# Define all 25+ commands and their outputs
COMMANDS = {
    "help": "Available commands: help, clear, whoami, current_time, echo [text], list_files, sys_info, secret_data, uptime, date, version, users, history, reboot, shutdown, ping, status, man, about, connect, disconnect, search [query], calc [expr], logout, exit, pwd, ls, cat, touch, mkdir, rmdir, cd",
    "clear": "", # Handled by JS
    "whoami": lambda: f"Current user: {session['username']}",
    "current_time": lambda: "The current time is " + os.popen('date +%H:%M:%S').read().strip(),
    "list_files": lambda: os.popen('ls -F Project/').read(),
    "sys_info": lambda: "OS: Linux/Windows/macOS (simulated)<br>Kernel: 5.10.0-std<br>Architecture: x86_64",
    "secret_data": "4dm1n_p455w0rd_15_n0t_h3r3",
    "uptime": lambda: "System uptime: 42 days, 3 hours, 15 minutes",
    "date": lambda: os.popen('date').read().strip(),
    "version": "Simulated OS v1.0.1",
    "users": "ADMIN, normal_user_1, normal_user_2",
    "history": "1. login, 2. help, 3. list_files, 4. whoami, 5. history",
    "reboot": "System rebooting... (simulated)",
    "shutdown": "System shutting down... Goodbye.",
    "ping": "Pinging 127.0.0.1... Reply from 127.0.0.1: bytes=32 time<1ms TTL=128",
    "status": "System status: OPERATIONAL",
    "man": "Man pages: Not implemented in this simulation.",
    "about": "This is a simulated terminal interface for a Flask web application.",
    "connect": "Connecting... Connected to mock network.",
    "disconnect": "Disconnecting... Disconnected.",
    "pwd": lambda: os.getcwd(),
    "ls": lambda: os.popen('ls').read(),
    "cat": "Usage: cat [filename] - Not fully functional",
    "touch": "Usage: touch [filename] - Not fully functional",
    "mkdir": "Usage: mkdir [dirname] - Not fully functional",
    "rmdir": "Usage: rmdir [dirname] - Not fully functional",
    "cd": "Usage: cd [directory] - Not fully functional",
    "echo": lambda text: text,
    "search": lambda query: f"Searching for: {query}",
    "calc": lambda expr: f"Result: {eval(expr)}" if all(c in "0123456789+-*/()." for c in expr) else "Error: Invalid expression",
    "exit": "Logging out...", # Handled by JS redirect
    "logout": "Logging out...", # Handled by JS redirect
}

@app.route('/api/terminal', methods=['POST'])
def api_terminal():
    if session.get('role') != 'admin':
        return jsonify({"output": "Unauthorized access to terminal API."}), 403
    
    command_input = request.json.get('command', '').strip().lower()
    parts = command_input.split(maxsplit=1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    
    if command in COMMANDS:
        output = COMMANDS[command]
        if callable(output):
            if command in ["echo", "search", "calc"]:
                response = output(args)
            else:
                response = output()
        else:
            response = output
        return jsonify({"output": response})
    else:
        return jsonify({"output": f"Command not found: {command_input}. Type 'help' for a list of commands."})

if __name__ == '__main__':
    init_db()
    add_initial_admin()
    app.run(debug=True)
