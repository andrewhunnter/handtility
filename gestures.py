import mediapipe as mp

def recognize_gesture(landmarks):
    """
    Recognizes gestures based on hand landmarks.
    Gestures:
    - THUMBS_UP: Thumb pointing up, other fingers closed
    - THUMBS_DOWN: Thumb pointing down, other fingers closed
    """
    thumb_tip = landmarks[mp.solutions.hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp.solutions.hands.HandLandmark.THUMB_IP]
    index_tip = landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP]
    
    # Check if fingers are closed (except thumb)
    fingers_closed = index_tip.y > index_pip.y
    
    # Thumbs Up: thumb tip is above thumb IP joint
    if fingers_closed and thumb_tip.y < thumb_ip.y:
        return "THUMBS_UP"
    
    # Thumbs Down: thumb tip is below thumb IP joint
    if fingers_closed and thumb_tip.y > thumb_ip.y:
        return "THUMBS_DOWN"
    
    return "UNKNOWN"
