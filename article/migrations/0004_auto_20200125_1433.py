# Generated by Django 2.1.5 on 2020-01-25 14:33

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('article', '0003_auto_20200120_1259'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ArticleColum',
            new_name='ArticleColumn',
        ),
    ]
