from django.db import models

class Workshop(models.Model):
    workshop_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    tutor = models.ForeignKey(
        'tutors.Tutor',
        on_delete=models.CASCADE
    )
    max_capacity = models.IntegerField()

    def __str__(self):
        return f"Workshop: {self.name} (Tutor: {self.tutor})"


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
