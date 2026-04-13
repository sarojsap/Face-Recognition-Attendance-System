import face_recognition
import os
from PIL import Image
import numpy as np
import cv2

IMAGE_FOLDER = r"C:\Users\saroj\Documents\FaceRecognition Attendance\chris_images"

# We will store the known encodings and their corresponding names here
known_face_encodings = []
known_face_names = []

def load_image_safe(file_path):
    try:
        img = Image.open(file_path).convert("RGB")
        img_array = np.array(img)
        if img_array.dtype != np.uint8:
            img_array = img_array.astype(np.uint8)
        return img_array
    except Exception as e:
        print(f"Image load failed: {e}")
        return None

def process_images(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"\nProcessing: {file_name}")
            image = load_image_safe(file_path)

            if image is None:
                continue

            try:
                # Get locations and encodings
                face_locations = face_recognition.face_locations(image)
                encodings = face_recognition.face_encodings(image, face_locations)

                if encodings:
                    # --> We append the encoding to our global list
                    known_face_encodings.append(encodings[0])
                    # --> We assume the images in this folder are of "Saroj"
                    known_face_names.append("Saroj") 
                    print(f"Loaded encoding for {file_name}")
                else:
                    print("No face found")

            except Exception as e:
                print(f"Face processing error: {e}")

# 1. Load the known faces first
print("Loading known faces...")
process_images(IMAGE_FOLDER)
print("Finished loading faces. Starting webcam...")

# 2. Start the Live Camera
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    
    # Resize and convert color
    resized_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    
    # Find all faces and encodings in the CURRENT live frame
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    live_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations)

    # --> LOOP through every face found in the live frame
    # zip() lets us loop through locations and encodings at the same time
    for face_encoding, face_location in zip(live_encodings, face_locations):
        
        # See if the face matches any known faces
        # matches will be a list of True/False, e.g., [True, False, False]
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        
        # Default name if no match is found
        name = "Unknown"

        # If there is a True in the matches list, we found our person!
        if True in matches:
            first_match_index = matches.index(True) # Find where the True is
            name = known_face_names[first_match_index] # Get the name from that index

        # --> NOW we unpack the coordinates for this specific face
        top, right, bottom, left = face_location

        # Scale them back up since we shrank the frame to 1/4
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)

    # Show the video
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()