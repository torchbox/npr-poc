# Generated by Django 2.1.8 on 2019-04-30 10:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import wagtail.core.models
import wagtail.search.index


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('podcasts', '0006_auto_20190426_0733'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('file', models.FileField(upload_to='media', verbose_name='file')),
                ('type', models.CharField(choices=[('audio', 'Audio file'), ('video', 'Video file')], max_length=255)),
                ('width', models.PositiveIntegerField(blank=True, null=True, verbose_name='width')),
                ('height', models.PositiveIntegerField(blank=True, null=True, verbose_name='height')),
                ('thumbnail', models.FileField(blank=True, upload_to='media_thumbnails', verbose_name='thumbnail')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('duration', models.DecimalField(decimal_places=2, editable=False, max_digits=10, null=True)),
                ('bitrate', models.PositiveIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('sample_rate', models.PositiveIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('channels', models.PositiveSmallIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('mime_type', models.CharField(blank=True, editable=False, max_length=20)),
                ('transcript', models.TextField(blank=True, editable=False)),
                ('collection', models.ForeignKey(default=wagtail.core.models.get_root_collection_id, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Collection', verbose_name='collection')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text=None, through='taggit.TaggedItem', to='taggit.Tag', verbose_name='tags')),
                ('uploaded_by_user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploaded by user')),
            ],
            options={
                'verbose_name': 'media',
                'abstract': False,
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.RemoveField(
            model_name='audiomedia',
            name='collection',
        ),
        migrations.AlterField(
            model_name='episodeenclosure',
            name='media',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='podcasts.CustomMedia'),
        ),
        migrations.DeleteModel(
            name='AudioMedia',
        ),
    ]