from django.db import models

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    id_number = models.IntegerField(unique=True)
    autonomy_level = models.CharField(
        max_length=20,
        choices=[
            ('1', 'Nivel 1'),
            ('2', 'Nivel 2'),
            ('3', 'Nivel 3'),
        ],
    )
    extended_vacation = models.BooleanField(default=False)
    grade = models.CharField(
        max_length=20,
        choices=[
            ('primero', 'Primero'),
            ('segundo', 'Segundo'),
            ('tercero', 'Tercero'),
            ('cuarto', 'Cuarto'),
            ('quinto', 'Quinto'),
            ('sexto', 'Sexto'),
            ('septimo', 'Séptimo'),
            ('octavo', 'Octavo'),
            ('noveno', 'Noveno'),
            ('decimo', 'Décimo'),
            ('once', 'Once'),
        ],
    )

    def __str__(self):
        return f"{self.name} {self.lastname} (ID: {self.student_id}) (Grado: {self.grade})"
