# Generated by Django 4.2.6 on 2023-11-27 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_course_total_seats_remove_course_used_seats_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='section_id',
            field=models.CharField(default=0, max_length=100, unique=True),
        ),
    ]