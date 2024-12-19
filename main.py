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
COOLDOWN_DURATION = 2.5  # 2.5 second cooldown between gestures
last_gesture_time = 0
gesture_count = 0  # Track total gestures
cooldown_start_time = 0
is_in_cooldown = False

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

def add_ui_overlay(frame, gesture_count, is_in_cooldown, time_remaining):
    height, width = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    line_color = (100, 100, 100)
    
    # Add semi-transparent overlay at the top
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 60), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
    
    # Add gesture count (top left)
    cv2.putText(frame, f"Gestures: {gesture_count}", (20, 40), font, 0.8, (255, 255, 255), 1)
    
    # Add cooldown indicator (top right)
    if is_in_cooldown:
        cooldown_text = f"Cooldown: {time_remaining:.1f}s"
        cv2.putText(frame, cooldown_text, (width - 200, 40), font, 0.8, (0, 0, 255), 1)
    else:
        cv2.putText(frame, "Ready", (width - 200, 40), font, 0.8, (0, 255, 0), 1)
    
    # Add separator line
    cv2.line(frame, (0, 60), (width, 60), line_color, 1)
    
    # Add gesture key (bottom)
    cv2.putText(frame, "👍 = Split Left", (20, height - 120), font, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "👎 = Split Right", (20, height - 90), font, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "☝️ = Option + 1", (20, height - 60), font, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "✌️ = Option + 2", (20, height - 30), font, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "🤟 = Option + 3", (width - 200, height - 60), font, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "🖖 = Option + 4", (width - 200, height - 30), font, 0.6, (255, 255, 255), 1)
    
    return frame

def main():
    # Check permissions before proceeding
    if not check_permissions():
        sys.exit(1)
        
    cap = cv2.VideoCapture(0)
    last_gesture = "UNKNOWN"  # Track last gesture to prevent repeated triggers
    
    # Initialize gesture count and cooldown
    global gesture_count, last_gesture_time
    
    # Fix: Initialize gesture_count as an integer instead of a dictionary
    gesture_count = 0  # Changed from gesture_count = {}
    is_in_cooldown = False
    cooldown_start_time = 0
    
    print("Press 'q' to quit.")
    print("Gestures:")
    print("- Thumbs Up: Option + A (left split)")
    print("- Thumbs Down: Option + L (right split)")
    print("- One Finger: Option + 1")
    print("- Two Fingers: Option + 2")
    print("- Three Fingers: Option + 3")
    print("- Four Fingers: Option + 4")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Add UI overlay
        frame = add_ui_overlay(frame, gesture_count, is_in_cooldown, COOLDOWN_DURATION - (time.time() - cooldown_start_time))

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                gesture = recognize_gesture(hand_landmarks.landmark)
                
                # Check cooldown and gesture change
                current_time = time.time()
                time_since_last = current_time - last_gesture_time
                
                # Update cooldown status
                is_in_cooldown = time_since_last < COOLDOWN_DURATION
                time_remaining = COOLDOWN_DURATION - time_since_last if is_in_cooldown else 0
                
                if not is_in_cooldown and gesture != last_gesture:
                    if gesture == "THUMBS_UP":
                        press_with_option('a')
                        print("Triggered: Option + A")
                        gesture_count += 1
                    elif gesture == "THUMBS_DOWN":
                        press_with_option('l')
                        print("Triggered: Option + L")
                        gesture_count += 1
                    elif gesture == "ONE_FINGER":
                        press_with_option('1')
                        print("Triggered: Option + 1")
                        gesture_count += 1
                    elif gesture == "TWO_FINGERS":
                        press_with_option('2')
                        print("Triggered: Option + 2")
                        gesture_count += 1
                    elif gesture == "THREE_FINGERS":
                        press_with_option('3')
                        print("Triggered: Option + 3")
                        gesture_count += 1
                    elif gesture == "FOUR_FINGERS":
                        press_with_option('4')
                        print("Triggered: Option + 4")
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
