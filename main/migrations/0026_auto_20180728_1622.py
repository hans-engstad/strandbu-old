# Generated by Django 2.0 on 2018-07-28 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20180728_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminsettings',
            name='max_from_date',
            field=models.IntegerField(default=365, help_text='Max days from today that customer can book cabin.'),
        ),
    ]
