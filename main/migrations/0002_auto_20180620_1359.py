# Generated by Django 2.0.6 on 2018-06-20 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cabin',
            name='images',
            field=models.ManyToManyField(blank=True, to='main.CabinImage'),
        ),
        migrations.AlterField(
            model_name='cabinimage',
            name='img',
            field=models.ImageField(upload_to='cabins/'),
        ),
    ]
