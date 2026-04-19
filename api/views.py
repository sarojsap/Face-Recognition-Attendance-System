import face_recognition
import numpy as np
from PIL import Image
from datetime import date

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
                # Find which employee matched
                match_index = matches.index(True)
                matched_employee = employees[match_index]

                # 6. Mark Attendance!
                # get_or_create checks if they already checked in TODAY. 
                # If not, it creates the record.
                attendance, created = Attendance.objects.get_or_create(
                    employee=matched_employee,
                    date=date.today()
                )

                if created:
                    return Response({
                        "status": "success", 
                        "message": f"Check-in successful for {matched_employee.name}",
                        "employee_id": matched_employee.employee_id
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        "status": "success", 
                        "message": f"{matched_employee.name} is already checked in today.",
                        "employee_id": matched_employee.employee_id
                    }, status=status.HTTP_200_OK)

            else:
                return Response({"error": "Face not recognized. Unknown person."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)