# Generated by Django 5.0.4 on 2024-12-19 17:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0002_alter_userattendance_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="userattendance",
            name="time",
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AlterField(
            model_name="userattendance",
            name="date",
            field=models.DateField(auto_now_add=True),
        ),
    ]
