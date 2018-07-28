# Generated by Django 2.0 on 2018-07-28 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20180728_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminsettings',
            name='max_date_span',
            field=models.IntegerField(default=365, help_text='Max days for booking'),
        ),
        migrations.AddField(
            model_name='adminsettings',
            name='max_to_date',
            field=models.IntegerField(default=365, help_text='Max days from today for to_date that customer can book cabin.'),
        ),
        migrations.AlterField(
            model_name='adminsettings',
            name='max_from_date',
            field=models.IntegerField(default=364, help_text='Max days from today for from_date that customer can book cabin.'),
        ),
        migrations.AlterField(
            model_name='adminsettings',
            name='min_from_date',
            field=models.IntegerField(default=1, help_text='Min days from today for from_date that customer can book cabin.'),
        ),
    ]