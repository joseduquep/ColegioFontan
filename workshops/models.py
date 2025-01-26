#models.py de la app workshops
from django.db import models

class Workshop(models.Model):
    WORKSHOP_TYPES = [
        ('primary', 'Primaria'),
        ('high_school', 'Bachillerato'),
        ('collective', 'Colectivo'),
    ]
    workshop_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    tutor = models.ForeignKey(
        'tutors.Tutor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workshops'  # Esta línea permite acceder a los talleres desde el tutor
    )
    max_capacity = models.IntegerField(default=25)
    type = models.CharField(
        max_length=20,
        choices=WORKSHOP_TYPES,
        default='primary'
    )

    def __str__(self):
        return f"{self.name} {self.tutor or 'Sin asignar'}"



class Block(models.Model):
    block_id = models.AutoField(primary_key=True)
    students = models.ManyToManyField('students.Student', related_name='blocks', blank=True)
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    block_number = models.IntegerField(default=0)  # Asegúrate que sea entero, no string.
    type = models.CharField(max_length=20, default='primary')
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Block: (ID: {self.block_id}) {self.workshop} {self.day} ({self.start_time} - {self.end_time})"
