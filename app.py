# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for sessions

# Database connection function
def get_db():
    conn = sqlite3.connect('hw13.db')  # Replace with your database file path
    return conn

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Hardcoded credentials
            session['logged_in'] = True
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            flash('Invalid credentials. Please try again.')  # Flash error message
            return redirect(url_for('login'))  # Stay on login page if credentials are wrong
    return render_template('login.html')  # Render the login page on GET request

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login
    conn = get_db()  # Connect to the database
    students = conn.execute('SELECT * FROM students').fetchall()  # Query students
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()  # Query quizzes
    conn.close()
    return render_template('dashboard.html', students=students, quizzes=quizzes)  # Pass data to template

# Add Student Route
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        conn = get_db()
        conn.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))  # Redirect to dashboard after adding a student
    return render_template('add_student.html')  # Show add student form

# Add Quiz Route
@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        conn = get_db()
        conn.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)', (subject, num_questions, quiz_date))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))  # Redirect to dashboard after adding a quiz
    return render_template('add_quiz.html')  # Show add quiz form

# View Student's Quiz Results
@app.route('/student/<int:student_id>')
def student_results(student_id):
    if not session.get('logged_in'):  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    results = conn.execute('SELECT quizzes.id, quizzes.subject, quiz_results.score FROM quiz_results JOIN quizzes ON quiz_results.quiz_id = quizzes.id WHERE quiz_results.student_id = ?', (student_id,)).fetchall()
    conn.close()
    return render_template('student_results.html', student=student, results=results)

# Add Quiz Result Route
@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        conn = get_db()
        conn.execute('INSERT INTO quiz_results (student_id, quiz_id, score) VALUES (?, ?, ?)', (student_id, quiz_id, score))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))  # Redirect to dashboard after adding the result
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    conn.close()
    return render_template('add_result.html', students=students, quizzes=quizzes)  # Show add result form

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect root to login page

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

