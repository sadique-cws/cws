# Generated by Django 2.2 on 2020-05-27 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0012_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(choices=[('1', 'Pending'), ('2', 'Paid')], default='1', max_length=1),
        ),
    ]
