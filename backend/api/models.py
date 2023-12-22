from django.db import models

# Create your models here.

class Fairmodel(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=265)
    description = models.TextField()

class Fairmodel_Version(models.Model):
    version = models.CharField(max_length=200)
    onnx_model = models.TextField()
    fairmodel = models.ForeignKey(Fairmodel, on_delete=models.CASCADE)
    update_description = models.TextField()
    created_at = models.DateTimeField()