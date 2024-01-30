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
    metadata_id = models.CharField(max_length=255)
    update_description = models.TextField()
    model_type = models.CharField(choices=ModelType.choices, default=ModelType.DEFAULT, max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def has_model(self):
        output_path = Path('storage/' + str(self.fairmodel.id) + '/' + str(self.id))
        return isfile(output_path)