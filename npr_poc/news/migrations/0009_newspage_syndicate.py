# Generated by Django 2.1.8 on 2019-05-16 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_merge_20190516_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='syndicate',
            field=models.BooleanField(default=False, help_text='Allow this story to be shared across NPR stations'),
        ),
    ]
