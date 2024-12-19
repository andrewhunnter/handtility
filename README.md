# Hand Gesture Window Manager

A Python application that uses computer vision to detect hand gestures and control window splitting on your computer. The app uses your webcam to recognize thumbs up/down gestures and triggers keyboard shortcuts for window management.

## Features

- Real-time hand gesture recognition using MediaPipe
- Gesture-to-keyboard mapping for window management
- Visual feedback with UI overlay showing:
  - Gesture count
  - System status and cooldown
  - Gesture guide
- Built-in cooldown system to prevent accidental triggers
- Permission checking for keyboard control

## Supported Gestures

| Gesture | Action | Keyboard Shortcut |
|---------|--------|-------------------|
| 👍 Thumbs Up | Split window left | Option + A |
| 👎 Thumbs Down | Split window right | Option + L |

## Requirements

- Python 3.x
- OpenCV (`cv2`)
- MediaPipe
- pynput
- numpy

## Installation

1. Clone this repository
2. Install the required packages: 