# Generated by Django 4.2.6 on 2023-11-25 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_alter_course_sections"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="sections",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
