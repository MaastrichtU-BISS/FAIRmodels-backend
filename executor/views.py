from django.shortcuts import render
from django.http import HttpResponse
import logging
from rdflib import Graph, URIRef

from api.models import Fairmodel, FairmodelVersion
from executor.services import JSONLDParser

# Create your views here.
def index(request):
    """
    Render the index page which lists the available models.
    """
    return_value = [ ]
    models = Fairmodel.objects.all().order_by('-created_at')
    for model in models:
        model_version = FairmodelVersion.objects.filter(fairmodel=model).order_by('-created_at').first()

        parser = JSONLDParser(json_ld_object=model_version.metadata_json)

        return_value.append({
            'title': parser.get_value(predicate="http://purl.org/dc/terms/title"),
            'version_id': model_version.id,
            'description': parser.get_value(predicate="http://purl.org/dc/terms/description"),
            'version': model_version.version,
            'created_at': model_version.created_at
        })
    logging.debug(return_value)
    return render(request, 'index.html', context={'models': return_value})