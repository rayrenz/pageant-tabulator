# Generated by Django 2.0 on 2018-06-10 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pageant', '0002_auto_20180610_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='judge',
            field=models.ForeignKey(limit_choices_to={'role': 'j'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
