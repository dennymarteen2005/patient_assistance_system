from flask import Flask, render_template, jsonify, request
from database import init_db, get_active_alerts, resolve_alert, record_alert, cancel_patient_alerts
import os

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Initialize the database on startup
init_db()

@app.route('/')
def patient_dashboard():
    return render_template('patient.html')

@app.route('/nurse')
def nurse_dashboard():
    return render_template('nurse.html')

@app.route('/doctor')
def doctor_dashboard():
    return render_template('doctor.html')

@app.route('/family')
def family_dashboard():
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
    # Threaded mode allows multiple dashboards on multiple devices
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
