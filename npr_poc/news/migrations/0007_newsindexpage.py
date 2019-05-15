# Generated by Django 2.1.8 on 2019-05-16 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0042_auto_20190516_1535'),
        ('news', '0006_auto_20190509_2137'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]