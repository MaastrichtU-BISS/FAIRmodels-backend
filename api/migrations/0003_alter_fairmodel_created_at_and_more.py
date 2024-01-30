# Generated by Django 5.0.1 on 2024-01-30 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_fairmodelversion_model_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fairmodel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='fairmodelversion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='fairmodelversion',
            name='model_type',
            field=models.CharField(choices=[('', 'Default'), ('ONNX', 'Onnx'), ('PMML', 'Pmml')], default='', max_length=64),
        ),
    ]