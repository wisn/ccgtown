# Generated by Django 3.1.3 on 2020-11-10 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotators', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='password',
            field=models.CharField(max_length=60, null=True),
        ),
    ]
