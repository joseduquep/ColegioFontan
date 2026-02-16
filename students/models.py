#models.py de la app students
from django.db import models
from django.utils.timezone import now

class Student(models.Model):
    STATUS_CHOICES = [
        ('present', 'Presente'),
        ('absent', 'Ausente'),
        ('neutral', 'No llamado'),
    ]
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    id_number = models.BigIntegerField(unique=True)
    autonomy_level = models.IntegerField(
        choices=[
            (1, 'Nivel 1'),
            (2, 'Nivel 2'),
            (3, 'Nivel 3'),
        ],
        default=1,
    )
    extended_vacation = models.BooleanField(default=False)
    grade = models.IntegerField(
        choices=[
            (-3, 'PJ (Prejardín)'),
            (-2, 'J (Jardín)'),
            (-1, 'T (Transición)'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
            (6, '6'),
            (7, '7'),
            (8, '8'),
            (9, '9'),
            (10, '10'),
            (11, '11'),
        ],
        default=1,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='neutral'
    )
    workshop = models.ForeignKey('workshops.Workshop', on_delete=models.SET_NULL, null=True, blank=True)
    last_reset = models.DateTimeField(default=now) 
    rotation_workshop = models.CharField(max_length=200, blank=True, null=True)
    general_data = models.TextField("Datos Generales", null=True, blank=True, help_text="Información adicional del estudiante")



    def __str__(self):
        return f"{self.name} {self.lastname} (ID: {self.student_id}) (Grado: {self.grade})"
    
    def get_today_attendance_summary(self):
        """
        Helper para compatibilidad con código legacy.
        Retorna un resumen del estado de asistencia del día basado en los registros Attendance.
        """
        from django.utils import timezone
        today = timezone.now().date()
        attendances = self.attendance_set.filter(date=today)
        
        if not attendances.exists():
            return 'neutral'
        
        if attendances.filter(status='absent').exists():
            return 'absent'
        elif attendances.filter(status='present').count() == attendances.count():
            return 'present'
        return 'neutral'


class Attendance(models.Model):
    """
    Modelo de asistencia por bloque.
    Registra la asistencia de un estudiante en un bloque específico en una fecha determinada.
    """
    STATUS_CHOICES = [
        ('present', 'Presente'),
        ('absent', 'Ausente'),
        ('neutral', 'No llamado'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_set'
    )
    block = models.ForeignKey(
        'workshops.Block',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='neutral'
    )
    marked_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que marcó la asistencia"
    )
    marked_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'block', 'date')
        ordering = ['-date', 'block__block_number']
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
    
    def __str__(self):
        return f"{self.student.name} - {self.block.workshop.name} ({self.date}) - {self.get_status_display()}"

