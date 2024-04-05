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

class VariableLink(models.Model):

    class VariableType(models.TextChoices):
        INPUT = 'INPUT'
        OUTPUT = 'OUTPUT'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fairmodel_version = models.ForeignKey(FairmodelVersion, on_delete=models.CASCADE)
    variable_type = models.CharField(choices=VariableType.choices, default=VariableType.INPUT, max_length=64)

    # reference to field in metadata (to index in list Input/Outcome)
    field_metadata = models.CharField(max_length=255)
    # reference to field in pmml/onnx representation
    field_model = models.CharField(max_length=255)