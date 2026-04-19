from django.urls import path
from .views import MarkAttendanceView

urlpatterns = [
    path('mark-attendance/', MarkAttendanceView.as_view(), name='mark_attendance'),
]
