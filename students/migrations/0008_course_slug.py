# Generated by Django 2.2 on 2020-05-24 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_course_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='slug',
            field=models.SlugField(default='testing'),
            preserve_default=False,
        ),
    ]