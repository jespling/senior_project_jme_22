# Generated by Django 4.0.1 on 2022-02-14 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_songstat'),
    ]

    operations = [
        migrations.AddField(
            model_name='songstat',
            name='artist_id',
            field=models.CharField(default='none', max_length=200),
        ),
    ]
