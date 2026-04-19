from django.db import models

class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    face_encoding = models.JSONField(help_text="Stores the 128-d face encoding array")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(auto_now_add=True)
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Prevent double check-ins for the same day
        unique_together = ['employee', 'date']

        def __str__(self):
            return f"{self.employee.name} - {self.date}"