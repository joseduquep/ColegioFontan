# Generated by Django 5.0 on 2024-12-13 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('lastname', models.CharField(max_length=100)),
                ('id_number', models.IntegerField(unique=True)),
                ('autonomy_level', models.IntegerField(choices=[(1, 'Nivel 1'), (2, 'Nivel 2'), (3, 'Nivel 3')], default=1)),
                ('extended_vacation', models.BooleanField(default=False)),
                ('grade', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11')], default=1)),
            ],
        ),
    ]
