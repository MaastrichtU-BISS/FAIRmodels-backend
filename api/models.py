import uuid
from django.db import models
from django.contrib.auth.models import User

class Fairmodel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

class FairmodelVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fairmodel = models.ForeignKey(Fairmodel, on_delete=models.CASCADE)
    version = models.CharField(max_length=255)
    metadata_id = models.CharField(max_length=255)
    # onnx_model = models.BinaryField(blank=True)
    update_description = models.TextField()
    created_at = models.DateTimeField(auto_now=True)