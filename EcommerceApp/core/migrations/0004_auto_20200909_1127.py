# Generated by Django 3.1.1 on 2020-09-09 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_item_sale_state'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='sale_state',
            new_name='state',
        ),
    ]
