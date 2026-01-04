from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
from werkzeug.security import check_password_hash

from authlib.integrations.flask_client import OAuth
from flask import session, redirect, url_for


app = Flask(__name__)
app.secret_key = "super-secret-rvce-admin-key"  # REQUIRED

oauth = OAuth(app)

oauth.register(
    name='google',
    client_id='1017727354818-58hevd8laghdkj3u9pntbk00ehq54ojd.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


# --- DATABASE CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'ar_user',       
    'password': 'password123', 
    'database': 'campus_ar_db'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return None

# --- ROUTES ---

@app.route('/test_db')
def test_db():
    conn = get_db_connection()
    if conn:
        conn.close()
        return "DB OK"
    return "DB FAIL"

@app.route('/login')
def login_auth():
    return render_template('login.html')


@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect('/login')
    return render_template(
        "admin_dashboard.html",
        admin_email=session['admin']
    )

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user = token['userinfo']

    email = user['email']

    if not email.endswith('@rvce.edu.in'):
        return "Unauthorized", 403

    session['admin'] = email
    return redirect('/admin')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/admin/building")
def add_building():
    return render_template("form_building.html")

@app.route("/admin/room")
def add_room():
    return render_template("form_room.html")

@app.route("/admin/faculty")
def add_faculty():
    return render_template("form_faculty.html")

@app.route("/admin/event")
def add_event():
    return render_template("form_event.html")

@app.route("/admin/student")
def add_student():
    return render_template("form_student.html")

@app.route("/admin/student-note")
def add_student_note():
    return render_template("form_student_note.html")




@app.route('/')
def index():
    marker_id = request.args.get('marker_id', default=1, type=int)
    return render_template('index.html', marker_id=marker_id)


@app.route('/api/get_overlay_data/<int:marker_id>')
def get_overlay_data(marker_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # STEP A: Fetch Room & Building Details
        query_marker = """
            SELECT m.type, r.room_number, r.name as room_name, r.building_id, r.room_id
            FROM Markers m
            JOIN Rooms r ON m.room_id = r.room_id
            WHERE m.marker_id = %s
        """
        cursor.execute(query_marker, (marker_id,))
        room_data = cursor.fetchone()
        
        if not room_data:
            return jsonify({"error": "Marker not registered"}), 404

        # STEP B: Fetch Building Name
        cursor.execute("SELECT name FROM Buildings WHERE building_id = %s", (room_data['building_id'],))
        building = cursor.fetchone()
        building_name = building['name'] if building else "Unknown Building"

        # STEP C: Fetch Active Events
        query_events = """
            SELECT name, description, start_time, end_time
            FROM Events 
            WHERE room_id = %s AND end_time >= NOW()
            ORDER BY start_time ASC LIMIT 3
        """
        cursor.execute(query_events, (room_data['room_id'],))
        raw_events = cursor.fetchall()

        formatted_events = []
        for e in raw_events:
            s_str = e['start_time'].strftime('%I:%M %p') 
            e_str = e['end_time'].strftime('%I:%M %p')
            
            formatted_events.append({
                "name": e['name'],
                "description": e['description'],
                "start_time_str": s_str,
                "end_time_str": e_str
            })

        # STEP D: Build Response
        response_data = {
            "building_name": building_name,
            "room_name": room_data['room_name'],
            "room_number": room_data['room_number'],
            "marker_type": room_data['type'],
            "events": formatted_events # Send the formatted list
        }


        cursor.close()
        conn.close()
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    usn = data.get('usn')
    password = data.get('password')

    if not usn or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Students WHERE usn = %s", (usn,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return jsonify({"success": False, "message": "Invalid USN"}), 401

    # TEMP (since we inserted plaintext)
    if not check_password_hash(user['password_hash'], password):
        return jsonify({"success": False, "message": "Invalid password"}), 401


    return jsonify({"success": True})


@app.route('/api/notes/<int:marker_id>')
def get_notes(marker_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            note_id,
            content,
            usn,
            created_at
        FROM Student_Notes
        WHERE marker_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """
    cursor.execute(query, (marker_id,))
    notes = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(notes)


@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.json
    usn = data.get('usn')
    marker_id = data.get('marker_id')
    content = data.get('content')

    if not all([usn, marker_id, content]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO Student_Notes (usn, marker_id, content)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (usn, marker_id, content))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})


@app.route("/api/buildings", methods=["POST"])
def create_building():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 403
     
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Missing building name"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO Buildings (name) VALUES (%s)"
    cursor.execute(query, (name,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})

@app.route("/api/events", methods=["POST"])
def create_event():
    
    data = request.json

    name = data.get("name")
    room_id = data.get("room_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    description = data.get("description")


    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO Events (name, room_id, start_time, end_time, description)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, room_id, start_time, end_time, description))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})


@app.route("/api/rooms", methods=["POST"])
def create_room():
    
    data = request.json
    
    name = data.get("name")
    building_id = data.get("building_id")
    room_no = data.get("room_no")


    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO Rooms ( building_id,name,room_number)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (building_id,name,room_no))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})

@app.route("/api/faculty", methods=["POST"])
def create_faculty():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

    name = data.get("name")
    office_room_id = data.get("office_room_id")

    if not name or not office_room_id:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO Faculty (name, office_room_id)
        VALUES (%s, %s)
    """
    cursor.execute(query, (name, office_room_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True})


from werkzeug.security import generate_password_hash

@app.route("/api/students", methods=["POST"])
def create_student():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

    usn = data.get("usn")
    password = data.get("password")

    if not usn or not password:
        return jsonify({"error": "Missing fields"}), 400

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO Students (usn, password_hash)
            VALUES (%s, %s)
        """
        cursor.execute(query, (usn.upper(), password_hash))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)