from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'hascol_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, station_name TEXT, station_id TEXT, fuel_type TEXT, quantity INTEGER, urgency TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (username TEXT, password TEXT)''')
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO requests (station_name, station_id, fuel_type, quantity, urgency, status) VALUES (?, ?, ?, ?, ?, ?)",
              (data['stationName'], data['stationId'], data['fuelType'], data['quantity'], data['urgency'], 'Pending'))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        admin = c.fetchone()
        conn.close()
        if admin:
            session['admin'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests")
    requests = c.fetchall()
    conn.close()
    return render_template('admin.html', requests=requests)

@app.route('/update/<int:req_id>/<string:status>')
def update(req_id, status):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE requests SET status = ? WHERE id = ?", (status, req_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
