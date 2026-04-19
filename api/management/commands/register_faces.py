import os
import face_recognition
import numpy as np
from PIL import Image
from django.core.management.base import BaseCommand
from api.models import Employee

class Command(BaseCommand):
    help = 'Reads images from a folder, extracts encodings, and saves them to the DB'

    def handle(self, *args, **kwargs):
        # CHANGE THIS to your actual folder path
        IMAGE_FOLDER = r"C:\Users\saroj\Documents\FaceRecognition Attendance\images"

        for file_name in os.listdir(IMAGE_FOLDER):
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                
                # Extract name and ID from filename (e.g., Saroj_1001.jpg)
                try:
                    name_part, ext = os.path.splitext(file_name)
                    name, emp_id = name_part.split('_')
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Skipping {file_name}: Name it like 'Name_ID.jpg'"))
                    continue

                file_path = os.path.join(IMAGE_FOLDER, file_name)
                
                # Safely load image (Your awesome logic!)
                try:
                    img = Image.open(file_path).convert("RGB")
                    img_array = np.array(img)
                    if img_array.dtype != np.uint8:
                        img_array = img_array.astype(np.uint8)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to load {file_name}: {e}"))
                    continue

                # Get encoding
                face_locations = face_recognition.face_locations(img_array)
                encodings = face_recognition.face_encodings(img_array, face_locations)

                if encodings:
                    # CONVERT Numpy array to Python List so JSON can store it!
                    encoding_list = encodings[0].tolist()

                    # Save to Django Database
                    # update_or_create means it will create a new employee, 
                    # but if 1001 already exists, it just updates their face encoding!
                    employee, created = Employee.objects.update_or_create(
                        employee_id=emp_id,
                        defaults={
                            'name': name,
                            'face_encoding': encoding_list
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created new employee: {name} ({emp_id})"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Updated existing employee: {name} ({emp_id})"))
                else:
                    self.stdout.write(self.style.ERROR(f"No face found in {file_name}"))