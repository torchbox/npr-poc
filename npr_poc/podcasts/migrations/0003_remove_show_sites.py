# Generated by Django 2.1.8 on 2019-04-25 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0002_auto_20190425_0714'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='show',
            name='sites',
        ),
    ]
