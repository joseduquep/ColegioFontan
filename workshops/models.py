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
        return f"{self.name} {self.tutor or 'Sin asignar'}"


from django.db import models

class Block(models.Model):
    block_id = models.AutoField(primary_key=True)
    students = models.ManyToManyField('students.Student', related_name='blocks')
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Block: (ID: {self.block_id}) {self.workshop} {self.day} ({self.start_time} - {self.end_time})"

