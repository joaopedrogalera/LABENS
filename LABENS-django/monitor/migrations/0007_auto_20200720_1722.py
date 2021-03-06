# Generated by Django 2.2.2 on 2020-07-20 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0006_auto_20200720_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatorpot',
            name='fpTipo',
            field=models.CharField(choices=[('D', 'Delay'), ('A', 'Advance')], max_length=1),
        ),
        migrations.AlterUniqueTogether(
            name='fatorpot',
            unique_together={('campus', 'nome')},
        ),
    ]
