# Generated by Django 3.1.5 on 2021-03-03 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20210223_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='body',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]