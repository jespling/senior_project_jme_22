# Generated by Django 4.0.1 on 2022-02-21 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_trackstat_snippet'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
            ],
        ),
    ]
