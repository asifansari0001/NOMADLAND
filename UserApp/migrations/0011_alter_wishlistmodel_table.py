# Generated by Django 4.2.9 on 2024-04-07 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0010_alter_wishlistmodel_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='wishlistmodel',
            table='wishlist',
        ),
    ]
