# Generated by Django 2.0 on 2018-06-10 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pageant', '0003_auto_20180610_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='readonly',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='score',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pageant.Candidate'),
        ),
    ]