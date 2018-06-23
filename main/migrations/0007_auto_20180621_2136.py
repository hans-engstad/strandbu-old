# Generated by Django 2.0.6 on 2018-06-21 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_cabin_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('mail', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=30)),
                ('country_code', models.CharField(max_length=10)),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='from_date',
            field=models.DateField(verbose_name=50),
        ),
        migrations.AddField(
            model_name='booking',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.ContactInfo'),
        ),
    ]