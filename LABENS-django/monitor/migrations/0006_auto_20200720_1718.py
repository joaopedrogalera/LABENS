# Generated by Django 2.2.2 on 2020-07-20 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0005_auto_20200720_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatorpot',
            name='fpTipo',
            field=models.CharField(choices=[('D', 'delay'), ('A', 'Advance')], max_length=1),
        ),
        migrations.AlterField(
            model_name='fatorpot',
            name='fpUpdateStatus',
            field=models.CharField(choices=[('A', 'Applied'), ('U', 'Updated')], max_length=1),
        ),
    ]
