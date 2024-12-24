 # students/tasks.py
from celery import shared_task
from students.models import Student

@shared_task
def reset_student_status():
    Student.objects.update(status='neutral')
