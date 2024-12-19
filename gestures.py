import mediapipe as mp

def recognize_gesture(landmarks):
    """
    Recognizes gestures based on hand landmarks.
    Gestures:
    - THUMBS_UP: Thumb pointing up, other fingers closed
    - THUMBS_DOWN: Thumb pointing down, other fingers closed
    - ONE_FINGER: Index finger up, others closed
    - TWO_FINGERS: Index and middle fingers up, others closed
    - THREE_FINGERS: Index, middle, and ring fingers up, others closed
    - FOUR_FINGERS: All fingers up except thumb
    """
    # Get finger landmarks
    thumb_tip = landmarks[mp.solutions.hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp.solutions.hands.HandLandmark.THUMB_IP]
    
    # Get fingertip and pip (middle joint) landmarks for each finger
    index_tip = landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP]
    
    middle_tip = landmarks[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = landmarks[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP]
    
    ring_tip = landmarks[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = landmarks[mp.solutions.hands.HandLandmark.RING_FINGER_PIP]
    
    pinky_tip = landmarks[mp.solutions.hands.HandLandmark.PINKY_TIP]
    pinky_pip = landmarks[mp.solutions.hands.HandLandmark.PINKY_PIP]
    
    # Check if each finger is extended (tip is above pip)
    index_up = index_tip.y < index_pip.y
    middle_up = middle_tip.y < middle_pip.y
    ring_up = ring_tip.y < ring_pip.y
    pinky_up = pinky_tip.y < pinky_pip.y
    
    # Count extended fingers (excluding thumb)
    extended_fingers = sum([index_up, middle_up, ring_up, pinky_up])
    
    # Check if fingers are closed (except thumb)
    fingers_closed = not any([index_up, middle_up, ring_up, pinky_up])
    
    # Thumbs Up: thumb tip is above thumb IP joint and other fingers closed
    if fingers_closed and thumb_tip.y < thumb_ip.y:
        return "THUMBS_UP"
    
    # Thumbs Down: thumb tip is below thumb IP joint and other fingers closed
    if fingers_closed and thumb_tip.y > thumb_ip.y:
        return "THUMBS_DOWN"
    
    # Check for finger counting gestures
    if index_up and not (middle_up or ring_up or pinky_up):
        return "ONE_FINGER"
    elif index_up and middle_up and not (ring_up or pinky_up):
        return "TWO_FINGERS"
    elif index_up and middle_up and ring_up and not pinky_up:
        return "THREE_FINGERS"
    elif index_up and middle_up and ring_up and pinky_up:
        return "FOUR_FINGERS"
    
    return "UNKNOWN"
