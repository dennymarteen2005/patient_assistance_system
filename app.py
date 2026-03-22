from flask import Flask, render_template, Response, jsonify, request
from camera import VideoCamera, generate_frames
from database import init_db, get_active_alerts, resolve_alert

app = Flask(__name__)

# Initialize DB on startup
init_db()

# Camera instance
camera = VideoCamera()

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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

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
