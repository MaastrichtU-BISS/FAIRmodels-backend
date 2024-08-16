# Generated by Django 5.0.1 on 2024-08-09 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_variablelink_field_model_var_dim_end_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='variablelink',
            name='unique appversion',
        ),
        migrations.AddField(
            model_name='variablelink',
            name='categories',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='variablelink',
            name='data_type',
            field=models.CharField(choices=[('CATEGORICAL', 'Categorical'), ('NUMERICAL', 'Numerical')], max_length=16, null=True),
        ),
        migrations.AddConstraint(
            model_name='variablelink',
            constraint=models.UniqueConstraint(fields=('fairmodel_version_id', 'variable_type', 'field_metadata_var_id', 'field_model_var_name', 'field_model_var_dim_index', 'field_model_var_dim_start', 'field_model_var_dim_end'), name='unique variablelink'),
        ),
        migrations.AddField(
            model_name='variablelink',
            name='unit',
            field=models.CharField(max_length=100, null=True),
        ),
    ]