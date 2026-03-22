# Gesture-Based Smart Patient Assistance System

A complete offline, software-based solution designed for hospital environments. The system uses computer vision to detect patient hand gestures via a webcam, converting them into real-time alerts that are instantly synchronized across dedicated nursing, doctor, and family dashboards.

## Features
- **Offline & Local**: Powered by a local Flask server and SQLite database, ensuring guaranteed privacy and zero reliance on internet connectivity.
- **Computer Vision**: Utilizes OpenCV and Google's MediaPipe for highly accurate, real-time hand landmark detection.
- **Five Configured Gestures**:
  - ✊ **Closed fist**: Normal nurse call
  - 🖐️ **Four fingers raised**: Emergency alert
  - ☝️ **Index finger**: Normal assistance request
  - ✌️ **Index + middle finger**: Cancel alert
  - 👍 **Thumbs up**: Call family member
- **Multi-Dashboard Interface**:
  - **Patient View**: Displays live webcam stream and real-time gesture status.
  - **Nurse Station**: Monitors all incoming alerts.
  - **Doctor Central**: Filters for high-priority Emergency alerts (displays full room/ward details).
  - **Family Portal**: Filters for family call requests.
- **Web Audio Notifications**: Browser-native synthesized notification chimes (harsh high-pitch patterns for emergencies, standard double-beeps for normal alerts).
- **Mobile PWA Ready**: The system can be installed natively as a mobile app on Android/iOS via the browser's "Add to Home Screen" feature.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dennymarteen2005/patient_assistance_system.git
   ```
2. Install the necessary Python packages:
   ```bash
   pip install flask opencv-python mediapipe
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the centralized dashboards on the local network (replace `localhost` with the host computer's IP address if accessing from mobile):
   - `http://localhost:5000/` for Patient View
   - `http://localhost:5000/nurse` for Nurse Station
   - `http://localhost:5000/doctor` for Doctor Central
   - `http://localhost:5000/family` for Family Portal
