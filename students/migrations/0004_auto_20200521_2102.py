# Generated by Django 2.2 on 2020-05-21 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_auto_20200521_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='contact',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
