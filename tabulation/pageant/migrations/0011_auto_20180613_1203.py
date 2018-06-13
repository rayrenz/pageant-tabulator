# Generated by Django 2.0 on 2018-06-13 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pageant', '0010_auto_20180613_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talent',
            name='candidate',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pageant.Candidate'),
        ),
        migrations.AlterField(
            model_name='talent',
            name='weight',
            field=models.FloatField(default=0.2),
        ),
    ]
