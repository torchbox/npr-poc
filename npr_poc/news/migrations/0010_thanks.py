# Generated by Django 2.1.8 on 2019-05-17 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0042_auto_20190516_1535'),
        ('images', '0002_customimage_file_hash'),
        ('news', '0009_newspage_syndicate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Thanks',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('social_text', models.CharField(blank=True, max_length=255)),
                ('listing_title', models.CharField(blank=True, help_text='Override the page title used when this page appears in listings', max_length=255)),
                ('listing_summary', models.CharField(blank=True, help_text="The text summary used when this page appears in listings. It's also used as the description for search engines if the 'Search description' field above is not defined.", max_length=255)),
                ('thanks_heading', models.CharField(max_length=255)),
                ('thanks_body', models.TextField(blank=True)),
                ('listing_image', models.ForeignKey(blank=True, help_text='Choose the image you wish to be displayed when this page appears in listings', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.CustomImage')),
                ('social_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.CustomImage')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
    ]
