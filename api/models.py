import uuid
from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
from os.path import isfile

class Fairmodel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FairmodelVersion(models.Model):

    class ModelType(models.TextChoices):
        DEFAULT = ''
        ONNX = 'ONNX'
        PMML = 'PMML'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fairmodel = models.ForeignKey(Fairmodel, on_delete=models.CASCADE)
    version = models.CharField(max_length=255)
    metadata_id = models.CharField(max_length=255, null=True)
    metadata_json = models.JSONField(null=True)
    update_description = models.TextField()
    model_type = models.CharField(choices=ModelType.choices, default=ModelType.DEFAULT, max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    metadata_input_variables = models.JSONField(null=True)
    metadata_output_variables = models.JSONField(null=True)
    model_input_variables = models.JSONField(null=True)
    model_output_variables = models.JSONField(null=True)

    @property
    def has_model(self):
        output_path = Path('storage/' + str(self.fairmodel.id) + '/' + str(self.id))
        return isfile(output_path)

class VariableType(models.TextChoices):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

class DataType(models.TextChoices):
    CATEGORICAL = 'CATEGORICAL'
    NUMERICAL = 'NUMERICAL'

class VariableLink(models.Model):
    class Meta:    
        constraints = [
            models.UniqueConstraint(fields=[
                'fairmodel_version_id',
                'variable_type',
                'field_metadata_var_id',
                'field_model_var_name',
                'field_model_var_dim_index',
                'field_model_var_dim_start',
                'field_model_var_dim_end',
            ], name='unique variablelink')
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fairmodel_version = models.ForeignKey(FairmodelVersion, on_delete=models.CASCADE)
    variable_type = models.CharField(choices=VariableType.choices, default=VariableType.INPUT, max_length=64)

    # reference to field in metadata (to index in list Input/Outcome)
    field_metadata_var_id = models.CharField(max_length=255)
    # reference to field in pmml/onnx representation
    
    field_model_var_name = models.CharField(max_length=255)
    field_model_var_dim_index = models.IntegerField(null=True)
    field_model_var_dim_start = models.IntegerField(null=True)
    field_model_var_dim_end = models.IntegerField(null=True)

    data_type = models.CharField(choices=DataType.choices, null=True, max_length=16)
    # if data_type == categorical
    # [
    #   {
    #      "ontology": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C48719",
    #      "name": "T0 TNM Finding",
    #      "mapping": "1"
    #   },
    #   ...
    # ]
    categories = models.JSONField(null=True)