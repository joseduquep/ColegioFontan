from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from students.models import Student, Attendance
from workshops.models import Block
from django.utils.timezone import now

def reset_student_status():
    """
    Crea registros de Attendance 'neutral' para bloques activos sin registro.
    Ya no modifica student.status (campo legacy deprecado).
    Los registros históricos se mantienen permanentemente.
    """
    print(f"Inicializando registros de asistencia - {datetime.now()}")
    today = now().date()
    
    # Crear attendance 'neutral' para bloques activos sin registro
    blocks_created = 0
    for block in Block.objects.all():
        for student in block.students.all():
            _, created = Attendance.objects.get_or_create(
                student=student,
                block=block,
                date=today,
                defaults={'status': 'neutral'}
            )
            if created:
                blocks_created += 1
    
    print(f"Registros de asistencia inicializados: {blocks_created} nuevos registros para {today}")

def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(reset_student_status, 'cron', hour=20, minute=9)
    scheduler.start()
    print("Programador iniciado...")
