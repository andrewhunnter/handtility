import cv2
import mediapipe as mp
from gestures import recognize_gesture
from pynput.keyboard import Controller, Key
import time
import sys
from pynput import keyboard as kb
import numpy as np

# Initialize MediaPipe Hands and Keyboard Controller
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
keyboard = Controller()

# Add these variables after keyboard initialization
COOLDOWN_DURATION = 1.0  # 1 second cooldown
last_gesture_time = 0
gesture_count = 0  # Track total gestures

def press_with_option(key):
    """Helper function to press a key with the Option (Alt) modifier"""
    try:
        # Press and hold Alt/Option
        keyboard.press(Key.alt)
        
        # Small delay to ensure the modifier is registered
        time.sleep(0.1)
        
        # Press and release the key
        keyboard.press(key)
        keyboard.release(key)
        
        # Small delay before releasing Alt
        time.sleep(0.1)
        
        # Release Alt/Option
        keyboard.release(Key.alt)
        
        # Final delay to prevent too rapid succession
        time.sleep(0.2)
    
    except Exception as e:
        print(f"Error executing keystroke: {e}")
    
def check_permissions():
    """Check if the application has necessary permissions"""
    try:
        # Try to create a listener - this will fail if permissions aren't granted
        with kb.Events() as events:
            pass
        return True
    except Exception as e:
        print("Error: Unable to control keyboard. Please check accessibility permissions.")
        print("Go to System Preferences → Security & Privacy → Privacy → Accessibility")
        print(f"Technical details: {e}")
        return False

def add_ui_overlay(frame, gesture_count):
    # Get frame dimensions
    height, width = frame.shape[:2]
    
    # Create semi-transparent overlay for the top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 60), (33, 33, 33), -1)
    
    # Add gradient effect
    gradient = np.linspace(0.3, 0, 60)
    for i in range(60):
        overlay[i, :] = overlay[i, :] * gradient[i]
    
    # Blend the overlay
    alpha = 0.85
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Add gesture count with icon
    gesture_text = f"Gestures Detected: {gesture_count}"
    cv2.putText(frame, gesture_text, (20, 40), font, 0.7, (255, 255, 255), 2)
    
    # Add status indicator and text
    cooldown_remaining = max(0, COOLDOWN_DURATION - (time.time() - last_gesture_time))
    if cooldown_remaining > 0:
        status_color = (0, 165, 255)  # Orange
        status_text = f"Cooldown: {cooldown_remaining:.1f}s"
    else:
        status_color = (0, 255, 0)  # Green
        status_text = "Ready"
    
    # Draw status circle
    cv2.circle(frame, (width - 120, 30), 8, status_color, -1)
    
    # Add status text
    cv2.putText(frame, status_text, (width - 100, 40), font, 0.7, status_color, 2)
    
    # Add separator line with gradient
    line_color = (255, 255, 255, 64)
    cv2.line(frame, (0, 60), (width, 60), line_color, 1)
    
    # Add gesture key (bottom left)
    cv2.putText(frame, "👍 = Split Left", (20, height - 60), font, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "👎 = Split Right", (20, height - 30), font, 0.6, (255, 255, 255), 1)
    
    return frame

def main():
    # Check permissions before proceeding
    if not check_permissions():
        sys.exit(1)
        
    cap = cv2.VideoCapture(0)
    last_gesture = "UNKNOWN"  # Track last gesture to prevent repeated triggers
    
    # Initialize gesture count and cooldown
    global gesture_count, last_gesture_time
    
    print("Press 'q' to quit.")
    print("Gestures:")
    print("- Thumbs Up: Option + A (left split)")
    print("- Thumbs Down: Option + L (right split)")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Add UI overlay
        frame = add_ui_overlay(frame, gesture_count)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                gesture = recognize_gesture(hand_landmarks.landmark)
                
                # Check cooldown and gesture change
                current_time = time.time()
                if (gesture != last_gesture and 
                    gesture != "UNKNOWN" and  # Only trigger on valid gestures
                    current_time - last_gesture_time >= COOLDOWN_DURATION):
                    
                    if gesture == "THUMBS_UP":
                        press_with_option('a')
                        print("Triggered: Option + A")
                        gesture_count += 1
                    elif gesture == "THUMBS_DOWN":
                        press_with_option('l')
                        print("Triggered: Option + L")
                        gesture_count += 1
                    
                    last_gesture = gesture
                    last_gesture_time = current_time
                elif gesture == "UNKNOWN":
                    # Just update last_gesture without triggering a count
                    last_gesture = gesture

        # Reset last_gesture when no hand is detected, but don't count it as a gesture
        if not results.multi_hand_landmarks:
            last_gesture = "UNKNOWN"

        cv2.imshow('Hand Gesture App', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
