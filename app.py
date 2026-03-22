from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from database import init_db, get_active_alerts, resolve_alert, record_alert, cancel_patient_alerts, create_user, authenticate_user
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_hospital'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize the database on startup
init_db()

@app.route('/')
def index():
    if 'role' in session:
        return redirect(url_for(f"{session['role']}_dashboard"))
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username').strip() if request.form.get('username') else ''
    password = request.form.get('password')
    role = request.form.get('role')
    action = request.form.get('action') # 'login' or 'signup'
    
    if not username or not password:
        flash("Username and password are required.")
        return redirect(url_for('index'))
        
    if action == 'signup':
        success = create_user(username, password, role)
        if success:
            session['username'] = username
            session['role'] = role
            return redirect(url_for(f"{role}_dashboard"))
        else:
            flash("Username already exists! Pick another one or log in.")
            return redirect(url_for('index'))
            
    elif action == 'login':
        if authenticate_user(username, password, role):
            session['username'] = username
            session['role'] = role
            return redirect(url_for(f"{role}_dashboard"))
        else:
            flash("Invalid credentials or incorrect portal. Please try again.")
            return redirect(url_for('index'))
            
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/patient')
def patient_dashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('index'))
    return render_template('patient.html')

@app.route('/nurse')
def nurse_dashboard():
    if session.get('role') != 'nurse':
        return redirect(url_for('index'))
    return render_template('nurse.html')

@app.route('/doctor')
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('index'))
    return render_template('doctor.html')

@app.route('/family')
def family_dashboard():
    if session.get('role') != 'family':
        return redirect(url_for('index'))
    return render_template('family.html')

@app.route('/api/trigger', methods=['POST'])
def trigger_alert():
    data = request.json
    gesture = data.get('gesture')
    patient_id = data.get('patient_id')
    room_no = data.get('room_no')
    bed_no = data.get('bed_no')
    ward = data.get('ward_details')
    alert_type = data.get('alert_type')
    
    if gesture == 'Index+Middle':
        cancel_patient_alerts(patient_id)
        return jsonify({"status": "cancelled"})
    else:
        record_alert(patient_id, room_no, bed_no, ward, alert_type)
        return jsonify({"status": "triggered"})

@app.route('/api/alerts', methods=['GET'])
def fetch_alerts():
    alerts = get_active_alerts()
    return jsonify(alerts)

@app.route('/api/resolve/<int:alert_id>', methods=['POST'])
def api_resolve_alert(alert_id):
    resolve_alert(alert_id)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
