# Generated by Django 2.0 on 2018-07-04 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20180704_1149'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactinfo',
            old_name='mail',
            new_name='email',
        ),
        migrations.AddField(
            model_name='finalbooking',
            name='charge_id',
            field=models.CharField(max_length=128, null=True),
        ),
    ]