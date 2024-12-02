from django.db import models

class Workshop(models.Model):
    workshop_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # Asegúrate de que el nombre sea único
    tutor = models.ForeignKey(
        'tutors.Tutor',
        on_delete=models.SET_NULL,  # Si el tutor se elimina, el campo queda en null
        null=True,                  # Permite que el campo sea nulo
        blank=True                  # Permite que el campo esté vacío en formularios
    )
    max_capacity = models.IntegerField(default=25)

    def __str__(self):
        return f"Workshop: {self.name} (Tutor: {self.tutor or 'Sin asignar'})"


class Block(models.Model):
    block_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE
    )
    day = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()
    high_school = models.BooleanField(default=False)
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Block: {self.day} ({self.start_time} - {self.end_time})"
