from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from students.models import Student
from django.utils.timezone import now

def reset_student_status():
    print(f"Reseteando estados de estudiantes - {datetime.now()}")  # Debug
    students = Student.objects.all()
    for student in students:
        student.status = 'neutral'
        student.last_reset = now()
        student.save()

def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(reset_student_status, 'cron', hour=23, minute=12)
    scheduler.start()
    print("Programador iniciado...")  # Debug

