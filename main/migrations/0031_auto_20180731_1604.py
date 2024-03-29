# Generated by Django 2.0 on 2018-07-31 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20180731_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminsettings',
            name='booking_close_time',
            field=models.TimeField(default='18:00:00', help_text='Time booking will close, if min_from_date is 0. (if customer can book today).'),
        ),
    ]
