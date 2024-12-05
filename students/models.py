from django.db import models

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    id_number = models.IntegerField(unique=True)
    autonomy_level = models.IntegerField(
        choices=[  # Cambiar los valores a enteros
            (1, 'Nivel 1'),
            (2, 'Nivel 2'),
            (3, 'Nivel 3'),
        ],
        default=1,  # Si no se especifica, por defecto se asigna "Nivel 1"
    )
    extended_vacation = models.BooleanField(default=False)
    grade = models.IntegerField(  # Cambiar los valores a enteros
        choices=[
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
            (11, '11'),  # Cambiar 'once' a 11 para que sea numérico
        ],
        default=1,  # Por defecto se asigna "Primero"
    )
    workshop = models.ForeignKey('workshops.Workshop', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.lastname} (ID: {self.student_id}) (Grado: {self.grade})"
