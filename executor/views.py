from pathlib import Path
from django.shortcuts import render
from django.http import HttpResponse
import logging
from rdflib import Graph, URIRef
import onnxruntime as ort

from api.models import Fairmodel, FairmodelVersion, VariableLink
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

def executor(request, model_id):
    """
    Render the executor page for a given model.
    """
    model_version = FairmodelVersion.objects.get(id=model_id)
    parser = JSONLDParser(json_ld_object=model_version.metadata_json)
    logging.debug("==================================")
    logging.debug(model_version.metadata_input_variables)
    
    if request.method == 'GET':
        # Show the view to enter the input values
        return render(request, 'executor.html', context={'model_version': model_version, 'title': parser.get_value(predicate="http://purl.org/dc/terms/title")})
    elif request.method == 'POST':
        # Execute the model

        # retrieve the entered values
        entered_values = request.POST.dict()
        logging.debug("Entered values: ")
        logging.debug(entered_values)

        # Match the entered values with the model input variables and add them in the correct order
        variable_links = VariableLink.objects.filter(fairmodel_version=model_version).order_by("field_model_var_dim_start").all()
        input_numbers = { }
        logging.debug("================Loop over variable links================")
        for variable_link in variable_links:
            if variable_link.variable_type != VariableLink.VariableType.INPUT:
                continue
            logging.debug(variable_link)
            logging.debug(str(variable_link.field_metadata_var_id) + " | " + str(variable_link.field_model_var_name) + " | " + str(variable_link.field_model_var_dim_index) + " | " + str(variable_link.field_model_var_dim_start) + " | " + str(variable_link.field_model_var_dim_end) + " | " + entered_values[variable_link.field_metadata_var_id])
            if variable_link.field_model_var_name not in input_numbers:
                input_numbers[variable_link.field_model_var_name] = [[ ]]
            input_numbers[variable_link.field_model_var_name][0].append(float(entered_values[variable_link.field_metadata_var_id]))
        logging.debug(input_numbers)

        # Fetch the ONNX object from storage and execute it
        model_path = Path('storage/' + str(model_version.fairmodel.id) + '/' + str(model_version.id))
        onnx_session = ort.InferenceSession(str(model_path))
        onnx_output = onnx_session.run(None, input_numbers)
        logging.debug(onnx_output)
        onnx_output = onnx_output[1][0]
    
    # Show the results
    return render(request, 'executor.html', context={'model_version': model_version, 'title': parser.get_value(predicate="http://purl.org/dc/terms/title"), 'onnx_output': onnx_output})