# Generated by Django 3.1.5 on 2021-02-05 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='reason',
            field=models.TextField(blank=True),
        ),
    ]