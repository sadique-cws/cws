# Generated by Django 2.2 on 2020-05-21 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_auto_20200521_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='city',
            field=models.CharField(choices=[('PUR', 'PURNEA')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='date_of_birth',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='education_qualification',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='image',
            field=models.ImageField(null=True, upload_to='students/dp/'),
        ),
        migrations.AlterField(
            model_name='student',
            name='name_of_institute',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='state',
            field=models.CharField(choices=[('BR', 'BIHAR')], max_length=3, null=True),
        ),
    ]
