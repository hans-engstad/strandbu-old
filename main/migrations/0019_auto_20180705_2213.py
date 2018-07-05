# Generated by Django 2.0 on 2018-07-05 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20180704_1617'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='finalbooking',
            name='active',
        ),
        migrations.AddField(
            model_name='booking',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='finalbooking',
            name='charge_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
