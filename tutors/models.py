# models.py de la app tutors
from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from workshops.models import Block  # Importamos el modelo Block de workshops

class Tutor(models.Model):
    tutor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="tutor_profile"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


    def __str__(self):
        return f"Tutor: {self.user.username}"


class ScheduleTutor(models.Model):
    schedule_tutor_id = models.AutoField(primary_key=True)
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE
    )
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE
    )
    high_school = models.BooleanField(default=False)

    def __str__(self):
        return f"ScheduleTutor: Tutor ({self.tutor.tutor_id}) - Block ({self.block.block_id})"
