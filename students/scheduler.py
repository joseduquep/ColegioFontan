# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from students.models import Student
from django.utils.timezone import now

def reset_student_status():
    """
    Restablece el estado de los estudiantes y actualiza el campo last_reset
    """
    print(f"Reseteando estados de estudiantes - {datetime.now()}")  # Solo para ver la ejecución
    students = Student.objects.all()
    for student in students:
        student.status = 'neutral'
        student.last_reset = now()
        student.save()

def start_scheduler():
    """
    Inicia el programador para ejecutar la tarea todos los días a las 00:00
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(reset_student_status, 'cron', hour=0, minute=0)  # Configura para las 00:00
    scheduler.start()
