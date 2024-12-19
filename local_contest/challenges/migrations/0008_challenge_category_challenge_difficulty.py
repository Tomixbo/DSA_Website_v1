# Generated by Django 5.0.4 on 2024-05-04 16:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("challenges", "0007_definedfile_output_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="challenge",
            name="category",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="challenge",
            name="difficulty",
            field=models.IntegerField(
                choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1
            ),
        ),
    ]
