# Generated by Django 4.2.6 on 2023-12-02 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_course_credit_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursewatch',
            name='sent',
            field=models.BooleanField(default=False),
        ),
    ]
