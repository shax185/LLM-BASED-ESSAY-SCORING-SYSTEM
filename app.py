from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import configparser
import bcrypt
import json
from structure_service import generate_essay_structure, edit_essay_structure
from evaluation_service import evaluate_essay
from llm_config import llm  
from feedback_service import generate_feedback 
import ast
import re

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = config['app']['secret_key']

db_config = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database']
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Home
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')) and user['role'] == role:
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            return redirect(url_for('user_dashboard') if role == "user" else url_for('admin_dashboard'))

        return "Invalid credentials or role mismatch!"
    
    return render_template('auth/login.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        role = request.form.get('role')
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return "User already exists!"

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
            (username, hashed_password.decode('utf-8'), role)
        )
        conn.commit()

        user_id = cursor.lastrowid
        cursor.close()
        conn.close()

        session['username'] = username
        session['role'] = role
        session['user_id'] = user_id

        return redirect(url_for('user_dashboard') if role == "user" else url_for('admin_dashboard'))

    return render_template('auth/register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# User Dashboard
@app.route('/dashboard')
def user_dashboard():
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.id, r.topic, r.difficulty_level, r.structure, u.username AS created_by
        FROM rubrics r
        JOIN users u ON r.created_by = u.id
        ORDER BY r.created_at DESC
    """)
    topics = cursor.fetchall()

    # Parse structure from JSON string to dict
    for topic in topics:
        try:
            topic['structure'] = ast.literal_eval(topic['structure'])
        except:
            topic['structure'] = {}

    cursor.close()
    conn.close()

    return render_template('user/dashboard.html', topics=topics)


# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

# Generate Structure
@app.route('/generate_structure', methods=['POST'])
def generate_structure():
    data = request.get_json()
    topic = data.get('topic')
    difficulty_level = data.get('difficulty')

    raw = generate_essay_structure(topic, difficulty_level)

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if not match:
        return jsonify({"error": "Structure not found in LLM response", "raw": raw}), 400

    try:
        json_text = match.group(1)
        parsed = json.loads(json_text)
        structure = parsed.get("structure", {})
    except Exception as e:
        return jsonify({"error": "Failed to parse JSON structure", "details": str(e)}), 500

    return jsonify({ "structure": structure })

# Finalize Structure
@app.route('/finalize_structure', methods=['POST'])
def finalize_structure():
    data = request.get_json()
    topic = data.get('topic')
    difficulty_level = data.get('difficulty')
    structure = data.get('structure')
    created_by = session.get('user_id')

    if not all([topic, difficulty_level, structure, created_by]):
        return jsonify({"status": "fail", "error": "Missing required data"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rubrics (topic, difficulty_level, structure, created_by)
            VALUES (%s, %s, %s, %s)
        """, (
            topic,
            difficulty_level,
            json.dumps(structure),
            created_by
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "fail", "error": str(e)}), 500

# Make Edit
@app.route('/api/make_edit', methods=['POST'])
def make_edit():
    data = request.json
    original_structure = data.get('original_structure')
    current_structure = data.get('current_structure')
    suggested_edit = data.get('suggested_edit')

    try:
        raw_response = edit_essay_structure(
            original_structure=json.dumps(original_structure, indent=2),
            current_structure=json.dumps(current_structure, indent=2),
            user_edits=suggested_edit
        )

        print("=== RAW LLM EDIT RESPONSE ===")
        print(raw_response)

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
        if not match:
            return jsonify({"success": False, "error": "Edited structure not found in LLM output", "raw": raw_response})

        json_text = match.group(1)
        parsed = json.loads(json_text)

        if "updated_structure" not in parsed:
            return jsonify({"success": False, "error": "No 'updated_structure' key in LLM response.", "parsed": parsed})

        return jsonify({
            "success": True,
            "updated_structure": parsed["updated_structure"],
            "modifications": parsed.get("modifications", [])
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin_previous_work')
def admin_previous_work():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rubrics ORDER BY created_at DESC")
    rubrics = cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ Parse the structure JSON for each rubric
    for rubric in rubrics:
        try:
            rubric['parsed_structure'] = json.loads(rubric['structure'])
        except Exception as e:
            rubric['parsed_structure'] = {}

    return render_template("admin/admin_previous_work.html", rubrics=rubrics)


@app.route('/history')
def essay_history():
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.id AS submission_id, s.content AS essay, s.submitted_at, 
               r.topic, r.difficulty_level,
               f.content_score, f.grammar_score, f.structure_score, f.conclusion_score, 
               f.final_score, f.feedback_text
        FROM submissions s
        JOIN rubrics r ON s.rubric_id = r.id
        LEFT JOIN feedback f ON s.id = f.submission_id
        WHERE s.user_id = %s
        ORDER BY s.submitted_at DESC
    """, (user_id,))
    submissions = cursor.fetchall()

    # Parse feedback JSON if present
    for sub in submissions:
        if sub['feedback_text']:
            try:
                sub['feedback'] = json.loads(sub['feedback_text'])
            except:
                sub['feedback'] = {"error": "Invalid feedback format"}
        else:
            sub['feedback'] = {"note": "No feedback generated."}

    cursor.close()
    conn.close()

    return render_template('user/essay_history.html', submissions=submissions)


@app.route('/submit_essay/<int:rubric_id>', methods=['GET', 'POST'])
def submit_essay(rubric_id):
    if 'username' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get rubric info
    cursor.execute("SELECT * FROM rubrics WHERE id = %s", (rubric_id,))
    rubric = cursor.fetchone()

    if not rubric:
        cursor.close()
        conn.close()
        return "Rubric not found"

    # Convert JSON from DB to dict
    rubric_structure = json.loads(rubric['structure'])  # ✅ this must be a dict

    if request.method == 'POST':
        essay_text = request.form['essay']
        user_id = session['user_id']

        # Store the essay
        cursor.execute("""
            INSERT INTO submissions (user_id, rubric_id, content)
            VALUES (%s, %s, %s)
        """, (user_id, rubric_id, essay_text))
        submission_id = cursor.lastrowid
        conn.commit()

        # ✅ Evaluate essay
        scores = evaluate_essay(essay_text, rubric_structure)
        feedback_json = generate_feedback(essay_text, rubric_structure)

        # ✅ Insert into feedback table
        cursor.execute("""
            INSERT INTO feedback (submission_id, content_score, grammar_score, structure_score, conclusion_score, final_score, feedback_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            submission_id,
            scores['section_scores'].get('Content', {}).get('score', 0),
            scores['section_scores'].get('Grammar, Coherence & Readability', {}).get('score', 0),
            scores['section_scores'].get('Main Body', {}).get('score', 0),
            scores['section_scores'].get('Conclusion', {}).get('score', 0),
            scores.get('total_score', 0),
            json.dumps(feedback_json['feedback'])
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return render_template('user/submitessay.html', rubric=rubric, structure=rubric_structure,
                               feedback={"scores": scores, "text": feedback_json['feedback']})

    cursor.close()
    conn.close()
    return render_template('user/submitessay.html', rubric=rubric, structure=rubric_structure)



if __name__ == '__main__':
    app.run(debug=True)
