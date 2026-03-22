import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'hospital.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            room_no TEXT,
            bed_no TEXT,
            ward_details TEXT,
            alert_type TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def record_alert(patient_id, room_no, bed_no, ward_details, alert_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if there's already an active alert of THIS type for THIS patient to avoid spam
    cursor.execute('''
        SELECT id FROM alerts 
        WHERE patient_id = ? AND alert_type = ? AND status = 'Active'
    ''', (patient_id, alert_type))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute('''
            INSERT INTO alerts (patient_id, room_no, bed_no, ward_details, alert_type, status)
            VALUES (?, ?, ?, ?, ?, 'Active')
        ''', (patient_id, room_no, bed_no, ward_details, alert_type))
    
    conn.commit()
    conn.close()

def get_active_alerts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM alerts WHERE status = 'Active' ORDER BY timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]

def cancel_patient_alerts(patient_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE alerts SET status = 'Cancelled' WHERE patient_id = ? AND status = 'Active'
    ''', (patient_id,))
    conn.commit()
    conn.close()

def resolve_alert(alert_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE alerts SET status = 'Resolved' WHERE id = ?
    ''', (alert_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
