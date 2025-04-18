# Generated by Django 5.0 on 2024-12-16 13:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutors', '0003_remove_tutor_photo'),
        ('workshops', '0004_alter_block_block_number_alter_block_students'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workshop',
            name='tutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workshops', to='tutors.tutor'),
        ),
    ]
