# Generated by Django 2.1.8 on 2019-05-09 14:26

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20190509_1522'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPageNewsCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_pages', to='news.NewsCategory')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='news.NewsPage')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='newspagenewscategory',
            unique_together={('page', 'news_category')},
        ),
    ]
