# Generated by Django 2.0 on 2018-07-04 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20180704_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basemodel',
            name='polymorphic_ctype',
        ),
        migrations.RemoveField(
            model_name='childmodela',
            name='basemodel_ptr',
        ),
        migrations.RemoveField(
            model_name='childmodelb',
            name='basemodel_ptr',
        ),
        migrations.DeleteModel(
            name='BaseModel',
        ),
        migrations.DeleteModel(
            name='ChildModelA',
        ),
        migrations.DeleteModel(
            name='ChildModelB',
        ),
    ]
