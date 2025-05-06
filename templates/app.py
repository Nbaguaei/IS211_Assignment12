import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection function
def get_db():
    conn = sqlite3.connect('hw13.db')
    conn.row_factory = sqlite3.Row  # This helps to access columns by name
    return conn

# Function to check if the user is logged in
def is_logged_in():
    return 'logged_in' in session and session['logged_in'] == True

# Part II: Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'password':  # Hardcoded credentials
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Part III: Dashboard Route (View Students and Quizzes)
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    conn.close()
    
    return render_template('dashboard.html', students=students, quizzes=quizzes)

# Part IV: Add Student Route
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        if first_name and last_name:
            conn = get_db()
            conn.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            flash('All fields are required!')
    
    return render_template('add_student.html')

# Part V: Add Quiz Route
@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        
        if subject and num_questions and quiz_date:
            conn = get_db()
            conn.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)',
                         (subject, num_questions, quiz_date))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            flash('All fields are required!')
    
    return render_template('add_quiz.html')

# Part VI: View Student's Quiz Results
@app.route('/student/<int:id>')
def student_results(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    results = conn.execute('SELECT * FROM quiz_results WHERE student_id = ?', (id,)).fetchall()
    conn.close()
    
    if not student:
        flash('Student not found!')
        return redirect(url_for('dashboard'))
    
    return render_template('student_results.html', student=student, results=results)

# Part VII: Add Student's Quiz Result
@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        
        if student_id and quiz_id and score:
            conn.execute('INSERT INTO quiz_results (student_id, quiz_id, score) VALUES (?, ?, ?)', 
                         (student_id, quiz_id, score))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            flash('All fields are required!')
    
    return render_template('add_result.html', students=students, quizzes=quizzes)

if __name__ == '__main__':
    app.run(debug=True)
