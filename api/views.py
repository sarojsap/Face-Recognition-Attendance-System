import face_recognition
import numpy as np
from PIL import Image
from datetime import date

from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Employee, Attendance

class MarkAttendanceView(APIView):
    # This tells DRF that this API accepts file uploads
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # 1. Get the uploaded image from the request
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Convert uploaded file to numpy array for face_recognition
            img = Image.open(file_obj).convert("RGB")
            img_array = np.array(img)

            # 3. Find face and extract encoding from the uploaded image
            face_locations = face_recognition.face_locations(img_array)
            live_encodings = face_recognition.face_encodings(img_array, face_locations)

            if not live_encodings:
                return Response({"error": "No face detected in image"}, status=status.HTTP_400_BAD_REQUEST)

            # We only process the first face found to keep it simple
            live_encoding = live_encodings[0]

            # 4. Fetch all known employees and their encodings from the Database!
            employees = Employee.objects.all()
            if not employees.exists():
                return Response({"error": "No employees registered in database"}, status=status.HTTP_404_NOT_FOUND)

            # Convert DB JSON back to NumPy arrays
            known_encodings = [np.array(emp.face_encoding) for emp in employees]
            
            # 5. Compare faces
            matches = face_recognition.compare_faces(known_encodings, live_encoding)

            if True in matches:
                match_index = matches.index(True)
                matched_employee = employees[match_index]

                # 6. Smart Check-In / Check-Out Logic
                today = date.today()
                now = timezone.now()

                # Try to get today's record
                attendance = Attendance.objects.filter(employee=matched_employee, date=today).first()

                if not attendance:
                    # First time seeing them today -> CHECK IN
                    Attendance.objects.create(employee=matched_employee, date=today, time_in=now)
                    return Response({
                        "status": "success", 
                        "message": f"Welcome, {matched_employee.name}! Checked IN.",
                    }, status=status.HTTP_201_CREATED)
                
                else:
                    # Record exists! Calculate how long it's been since they checked in
                    time_since_check_in = now - attendance.time_in

                    # For testing, let's use 1 minute (60 seconds). 
                    # In production, this would be maybe 1 hour.
                    if time_since_check_in < timedelta(minutes=1):
                        return Response({
                            "status": "success", 
                            "message": f"{matched_employee.name} already checked in recently.",
                        }, status=status.HTTP_200_OK)
                    
                    else:
                        # It's been more than a minute -> CHECK OUT
                        attendance.time_out = now
                        attendance.save()
                        return Response({
                            "status": "success", 
                            "message": f"Goodbye, {matched_employee.name}! Checked OUT.",
                        }, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Unknown face."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)