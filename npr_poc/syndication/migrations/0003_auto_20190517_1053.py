# Generated by Django 2.1.8 on 2019-05-17 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syndication', '0002_syndicatednewspage_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='syndicatednewspage',
            options={'verbose_name_plural': 'Syndicated News'},
        ),
        migrations.AlterField(
            model_name='syndicatednewspage',
            name='story',
            field=models.CharField(db_index=True, max_length=255),
        ),
    ]
