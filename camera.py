import cv2
import mediapipe as mp
import time
from database import record_alert, cancel_patient_alerts

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Hardcoded Patient details for demo purposes
PATIENT_ID = "P-101"
ROOM_NO = "104"
BED_NO = "A2"
WARD = "General Ward"

def get_gesture(hand_landmarks):
    lm = hand_landmarks.landmark
    
    # Simple finger extension logic based on y-coordinates (assuming hand is upright)
    index_ext = lm[8].y < lm[6].y
    middle_ext = lm[12].y < lm[10].y
    ring_ext = lm[16].y < lm[14].y
    pinky_ext = lm[20].y < lm[18].y
    
    # Thumb logic: Check if thumb tip is above its joints and other fingers are folded
    thumb_up = (lm[4].y < lm[3].y and lm[4].y < lm[5].y and 
                not index_ext and not middle_ext and not ring_ext and not pinky_ext)
                
    if thumb_up:
        return "Thumbs Up"
        
    if not index_ext and not middle_ext and not ring_ext and not pinky_ext:
        return "Fist"
        
    if index_ext and middle_ext and ring_ext and pinky_ext:
        return "Four Fingers"
        
    if index_ext and not middle_ext and not ring_ext and not pinky_ext:
        return "Index"
        
    if index_ext and middle_ext and not ring_ext and not pinky_ext:
        return "Index+Middle"
        
    return None

class VideoCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.last_gesture = None
        self.gesture_start_time = 0
        self.gesture_duration_threshold = 2.0 # Hold gesture for 2 seconds
        self.cooldown_end = 0

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None

        # Mirror frame
        frame = cv2.flip(frame, 1) 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        current_gesture = None

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                current_gesture = get_gesture(hand_landmarks)
                break # Only use one hand

        current_time = time.time()
        
        # Debounce and trigger
        if current_time < self.cooldown_end:
            cv2.putText(frame, "Alert Triggered!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif current_gesture:
            cv2.putText(frame, f"Detecting: {current_gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            if current_gesture == self.last_gesture:
                if current_time - self.gesture_start_time > self.gesture_duration_threshold:
                    self.trigger_alert(current_gesture)
                    self.cooldown_end = current_time + 3.0 # Cooldown for 3 seconds
            else:
                self.last_gesture = current_gesture
                self.gesture_start_time = current_time
        else:
            self.last_gesture = None

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def trigger_alert(self, gesture):
        print(f"Triggering alert for: {gesture}")
        if gesture == "Fist":
            record_alert(PATIENT_ID, ROOM_NO, BED_NO, WARD, "Normal nurse call")
        elif gesture == "Four Fingers":
            record_alert(PATIENT_ID, ROOM_NO, BED_NO, WARD, "Emergency alert")
        elif gesture == "Index":
            record_alert(PATIENT_ID, ROOM_NO, BED_NO, WARD, "Normal assistance request")
        elif gesture == "Index+Middle":
            cancel_patient_alerts(PATIENT_ID)
        elif gesture == "Thumbs Up":
            record_alert(PATIENT_ID, ROOM_NO, BED_NO, WARD, "Call family member")

    def __del__(self):
        self.cap.release()

def generate_frames(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            time.sleep(0.1)
