# Generated by Django 4.0.4 on 2022-05-27 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]
