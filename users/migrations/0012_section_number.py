# Generated by Django 4.2.6 on 2023-11-28 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_section_section_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]