# Generated by Django 2.2.2 on 2020-08-04 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InvConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campus', models.CharField(max_length=2)),
                ('nome', models.CharField(max_length=4)),
                ('descri', models.TextField()),
                ('fp', models.DecimalField(decimal_places=2, max_digits=3)),
                ('fpTipo', models.CharField(choices=[('D', 'Delay'), ('A', 'Advance')], max_length=1)),
                ('fpMin', models.DecimalField(decimal_places=2, max_digits=3)),
                ('fpMax', models.DecimalField(decimal_places=2, max_digits=3)),
                ('limPot', models.IntegerField()),
                ('UpdateStatus', models.CharField(choices=[('A', 'Applied'), ('U', 'Updated')], max_length=1)),
                ('UpdateTime', models.DateTimeField()),
            ],
            options={
                'unique_together': {('campus', 'nome')},
            },
        ),
        migrations.CreateModel(
            name='InvConfigTokens',
            fields=[
                ('token', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('inverters', models.ManyToManyField(to='invConfig.InvConfig')),
            ],
        ),
    ]