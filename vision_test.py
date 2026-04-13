import face_recognition
import os
from PIL import Image
import numpy as np
import cv2

IMAGE_FOLDER = r"C:\Users\saroj\Documents\FaceRecognition Attendance\chris_images"

all_encodings = []
image_names = []

def load_image_safe(file_path):
    try:
        # Open image
        img = Image.open(file_path)

        # Convert to RGB (removes CMYK, RGBA, etc.)
        img = img.convert("RGB")

        # Convert to numpy array
        img_array = np.array(img)

        # Ensure dtype is uint8 (VERY IMPORTANT)
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
                # 🔹 Resize image to 1/4 for faster processing
                small_image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)

                # 🔹 Detect faces on resized image
                face_locations = face_recognition.face_locations(small_image)

                # 🔹 Get encodings from resized image
                encodings = face_recognition.face_encodings(small_image, face_locations)

                if encodings:
                    print(f"Found {len(encodings)} face(s)")

                    all_encodings.append(encodings[0])
                    image_names.append(file_name)

                else:
                    print("No face found")

            except Exception as e:
                print(f"Face processing error: {e}")


process_images(IMAGE_FOLDER)

print("\nSummary:")
print(f"Total images processed: {len(image_names)}")
print(f"Total encodings stored: {len(all_encodings)}")