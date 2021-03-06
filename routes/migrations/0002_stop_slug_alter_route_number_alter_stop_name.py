# Generated by Django 4.0.4 on 2022-05-04 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='slug',
            field=models.SlugField(default='qwe', unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='route',
            name='number',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='stop',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
