# Generated by Django 4.0.1 on 2022-02-20 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_songstat_img_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackstat',
            name='snippet',
            field=models.URLField(default='none'),
        ),
    ]