from django.db import models

class Workshop(models.Model):
    WORKSHOP_TYPES = [
        ('primary', 'Primaria'),
        ('high_school', 'Bachillerato'),
        ('collective', 'Colectivo'),
    ]


    workshop_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # Asegúrate de que el nombre sea único
    tutor = models.ForeignKey(
        'tutors.Tutor',
        on_delete=models.SET_NULL,  
        null=True,                  
        blank=True                  
    )
    max_capacity = models.IntegerField(default=25)
    type = models.CharField(
        max_length=20,
        choices=WORKSHOP_TYPES,
        default='primary'
    )

    def __str__(self):
        return f"Workshop: {self.name} (Tutor: {self.tutor or 'Sin asignar'})"


class Block(models.Model):
    block_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        null=True,                  
        blank=True 
    )
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Block: {self.workshop} {self.day} ({self.start_time} - {self.end_time})"
