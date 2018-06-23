# Generated by Django 2.0.6 on 2018-06-21 20:48

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20180621_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactinfo',
            name='country_code',
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='country',
            field=django_countries.fields.CountryField(default={'country': 'NO'}, max_length=2),
            preserve_default=False,
        ),
    ]
