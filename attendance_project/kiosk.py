import cv2
import face_recognition
import requests
import time

# API Settings
API_URL = 'http://127.0.0.1:8000/api/mark-attendance/'
COOLDOWN_SECONDS = 5  # Wait 5 seconds before sending another request

# Variables to track time and screen messages
last_request_time = 0
display_message = "Waiting for face..."

video_capture = cv2.VideoCapture(0)

print("Kiosk started. Press 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    
    # 1. Resize for fast detection
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # 2. ONLY detect locations (Let the server handle the heavy encodings!)
    face_locations = face_recognition.face_locations(rgb_small_frame)

    current_time = time.time()

    # 3. If a face is found AND we are not on cooldown
    if face_locations and (current_time - last_request_time) > COOLDOWN_SECONDS:
        display_message = "Processing..."
        
        # 4. Convert the CURRENT full-size frame to JPEG bytes in memory
        # (We don't need to save it to the hard drive to send it)
        success, buffer = cv2.imencode('.jpg', frame)
        if success:
            image_bytes = buffer.tobytes()
            
            # 5. Send the image to Django
            files = {'image': ('kiosk_snap.jpg', image_bytes, 'image/jpeg')}
            try:
                response = requests.post(API_URL, files=files)
                data = response.json()
                
                # Check what the server said
                if response.status_code in [200, 201]:
                    display_message = data.get("message", "Success!")
                    print(f"API Success: {display_message}")
                else:
                    display_message = data.get("error", "Unknown face")
                    print(f"API Error: {display_message}")
                    
            except Exception as e:
                print("Could not connect to server.")
                display_message = "Server offline"
                
            # Reset the cooldown timer
            last_request_time = time.time()

    # --- Drawing UI on the Kiosk Screen ---
    
    # Draw boxes around faces (just for visual feedback)
    for (top, right, bottom, left) in face_locations:
        top *= 4; right *= 4; bottom *= 4; left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Put the API response text at the bottom of the screen
    cv2.putText(frame, display_message, (20, frame.shape[0] - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow('Attendance Kiosk', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()