# Generated by Django 2.1.8 on 2019-04-26 06:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('podcasts', '0005_auto_20190425_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('media_file', models.FileField(upload_to='media')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('duration', models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True)),
                ('bitrate', models.PositiveIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('sample_rate', models.PositiveIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('channels', models.PositiveSmallIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('mime_type', models.CharField(blank=True, editable=False, max_length=20)),
                ('transcript', models.TextField(blank=True, editable=False)),
                ('collection', models.ForeignKey(default=wagtail.core.models.get_root_collection_id, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Collection', verbose_name='collection')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='episodeenclosure',
            options={'ordering': ['sort_order']},
        ),
        migrations.RemoveField(
            model_name='episode',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='bitrate',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='channels',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='media_file',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='mime_type',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='sample_rate',
        ),
        migrations.RemoveField(
            model_name='episodeenclosure',
            name='title',
        ),
        migrations.AddField(
            model_name='episodeenclosure',
            name='media',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='podcasts.AudioMedia'),
        ),
    ]
