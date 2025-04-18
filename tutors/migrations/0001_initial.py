# Generated by Django 5.0 on 2024-12-13 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleTutor',
            fields=[
                ('schedule_tutor_id', models.AutoField(primary_key=True, serialize=False)),
                ('high_school', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('tutor_id', models.AutoField(primary_key=True, serialize=False)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='tutors_photos/')),
            ],
        ),
    ]
