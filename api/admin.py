from django.contrib import admin
from .models import Employee, Attendance

admin.site.register(Employee)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee','time_in', 'time_out')