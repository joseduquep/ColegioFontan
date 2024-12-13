from django.db import models

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE
    )
    block = models.ForeignKey(
        'workshops.Block',
        on_delete=models.CASCADE
    )
    high_school = models.BooleanField(default=False)

    def __str__(self):
        return f"Schedule for Student: {self.student}"
