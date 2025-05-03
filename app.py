from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS departments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL
                        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS doctors (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT,
                            phone TEXT,
                            department_id INTEGER,
                            FOREIGN KEY(department_id) REFERENCES departments(id)
                        )''')
        conn.execute("INSERT INTO departments (name) VALUES ('Cardiology'), ('Neurology'), ('Pediatrics')")
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/doctors")
def index():
    conn = get_db_connection()
    doctors = conn.execute('''
        SELECT d.id, d.name, d.email, d.phone, departments.name as department
        FROM doctors d
        JOIN departments ON d.department_id = departments.id
    ''').fetchall()
    conn.close()
    return render_template("index.html", doctors=doctors)

@app.route("/add", methods=["GET", "POST"])
def add_doctor():
    conn = get_db_connection()
    departments = conn.execute("SELECT * FROM departments").fetchall()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department_id = request.form["department_id"]
        conn.execute("INSERT INTO doctors (name, email, phone, department_id) VALUES (?, ?, ?, ?)",
                     (name, email, phone, department_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_doctor.html", departments=departments)

@app.route('/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    conn = get_db_connection()
    doctor = conn.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,)).fetchone()
    departments = conn.execute('SELECT * FROM departments').fetchall()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department_id = request.form['department_id']
        conn.execute('UPDATE doctors SET name = ?, email = ?, phone = ?, department_id = ? WHERE id = ?',
                     (name, email, phone, department_id, doctor_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit_doctor.html', doctor=doctor, departments=departments)

@app.route('/delete/<int:doctor_id>')
def delete_doctor(doctor_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
