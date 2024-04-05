import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
from .models import Fairmodel, FairmodelVersion
from .serializers import FairmodelSerializer, FairmodelVersionSerializer
from pathlib import Path
from .services import MetadataCenterAPIService
from django.conf import settings
import traceback

# /
@api_view(['GET'])
def index(req):
    return Response({"Hello": "World"})

# /cedar_instances
@api_view(['GET'])
def cedar_instances(req):
    try:
        mc_service = MetadataCenterAPIService()
        page = req.GET.get('page', '1')
        if not page.isnumeric():
            return Response({'message': 'Page parameter is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        page = int(page)
        response = mc_service.get_instances(settings.METADATACENTER_INSTANCES_FOLDER_ID, page)
        return Response({'instances': response['resources']})
    except requests.RequestException as e:
        return Response({'message': 'An error occured when attempting to retrieve the instances from CEDAR'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# /model
@api_view(['GET', 'POST'])
def fairmodels_view(req):
    if req.method == 'GET':
        owned = req.GET.get('owned', '') == 'true'
        fairmodel = Fairmodel.objects.all().order_by('-created_at') if not owned else Fairmodel.objects.filter(user=req.user.id).order_by('-created_at')
        serialized = FairmodelSerializer(fairmodel, many=True)
        return Response({'fairmodels': serialized.data})
    elif req.method == 'POST':
        if not req.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        req.data['user'] = req.user.id
        serialized = FairmodelSerializer(data=req.data, context={ 'request': req})
        if serialized.is_valid():
            serialized.save()
            return Response({'message': "Successfully created", 'fairmodel': serialized.data})
        else:
            return Response({'message': 'Failed to create model', 'detail': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)

# /model/model_id
@api_view(['GET', 'PUT', 'DELETE'])
def fairmodel_view(req, model_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
    except Fairmodel.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)

    if req.method == 'GET':
        serialized = FairmodelSerializer(fairmodel)
        return Response({'fairmodel': serialized.data})
    
    elif req.method == 'PUT':
        if not req.user.is_authenticated or not req.user.id == fairmodel.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serialized = FairmodelSerializer(fairmodel, data=req.data, partial=True)
        if serialized.is_valid():
            serialized.save()
            return Response({'message': 'Updated successfully', 'fairmodel': serialized.data})
        else:
            return Response({'message': 'Failed to update model', 'detail': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    elif req.method == 'DELETE':
        if not req.user.is_authenticated or not req.user.id == fairmodel.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        fairmodel.delete()
        return Response({'message': 'Deleted successfully'})

# /model/model_id/version/
@api_view(['GET', 'POST'])
def modelversions_view(req, model_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
    except Fairmodel.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)
    
    if not req.user.is_authenticated or not req.user.id == fairmodel.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if req.method == 'GET':
        fairmodel_versions = FairmodelVersion.objects.filter(fairmodel=fairmodel).all().order_by('-created_at')
        serialized = FairmodelVersionSerializer(fairmodel_versions, many=True)
        return Response({'fairmodelversions': serialized.data })
    
    elif req.method == 'POST':
        last_version = FairmodelVersion.objects.filter(fairmodel=fairmodel).order_by('-created_at').first()
        new_version = list(map(int, str(last_version.version).split('.'))) if last_version else [0,0,0]

        update_type = req.data['update_type']

        if not len(new_version) == 3:
            raise Exception("Version-number not in semantic format")
        if update_type == 'major':
            new_version[0] += 1
            new_version[1] = 0
            new_version[2] = 0
        elif update_type == 'minor':
            new_version[1] += 1
            new_version[2] = 0
        elif update_type == 'patch':
            new_version[2] += 1
        else:
            return Response({"message": "Invalid update-type"}, status=status.HTTP_400_BAD_REQUEST)

        new_version = '.'.join(map(str, new_version))

        req.data['version'] = new_version
        req.data['fairmodel'] = fairmodel.id
        del req.data['update_type']
        serialized = FairmodelVersionSerializer(data=req.data, context={'request': req})
        if serialized.is_valid():
            serialized.save()
            return Response({'message': "Successfully created", 'version': serialized.data})
        else:
            return Response({'message': 'Failed to create model', 'detail': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)

# /model/model_id/version/version_id
@api_view(['GET', 'PUT', 'DELETE'])
def modelversion_view(req, model_id, version_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
        fairmodel_version = FairmodelVersion.objects.get(pk=version_id)
    except Fairmodel.DoesNotExist or FairmodelVersion.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)

    # user is authenticated
    # user is owner of the model
    # version belongs to model
    if not req.user.is_authenticated or not req.user.id == fairmodel.user.id or not fairmodel_version.fairmodel.id == model_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    if req.method == "GET":
        serialized_version = FairmodelVersionSerializer(fairmodel_version)
        return Response({'fairmodelversion': serialized_version.data })

    elif req.method == "PUT":
        if fairmodel_version.metadata_id:
            return Response({'message': 'This version already has "metadata_id" and cannot be updated again. Create a new version instead.'}, status=status.HTTP_400_BAD_REQUEST)
        if not req.data['metadata_id']:
            return Response({'message': 'Expected parameter: only "metadata_id"'}, status=status.HTTP_400_BAD_REQUEST)

        # todo: fetch instance metadata and store
        try:
            mc_service = MetadataCenterAPIService()
            instance_metadata = mc_service.get_instance(req.data['metadata_id'])
        except requests.HTTPError as e:
            json = e.response.json()
            if json['message'] and json['message'] == 'You do not have read access to the artifact':
                return Response({'message': 'Could not find the given resource'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'An error occured when attempting to retrieve the resource.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if '@id' not in instance_metadata :
            return Response({'message': 'The given instance could not be parsed.'})
        
        def map_mdc_vars(row):
            return {'id': row['@id'], 'name': row['rdfs:label']}
        
        # TODO: write generic class that infers variables from ONNX or in future PMML models

        metadata_input_variables = list(map(map_mdc_vars, instance_metadata['Input']))
        metadata_output_variables = map_mdc_vars(instance_metadata['Outcome'])
        if isinstance(metadata_output_variables, object):
            metadata_output_variables = [metadata_output_variables]
        
        if len(metadata_input_variables) < 1:
            return Response({'message': 'Instance must contain atleast one input variable'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(metadata_output_variables) < 1:
            return Response({'message': 'Instance must contain atleast one output variable'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_version = FairmodelVersionSerializer(fairmodel_version, data={
            'metadata_id': req.data['metadata_id'],
            'metadata_json': instance_metadata,
            'metadata_input_variables': metadata_input_variables,
            'metadata_output_variables': metadata_output_variables,
        }, partial=True)

        if serialized_version.is_valid():
            serialized_version.save()
            return Response({'message': 'Update succeded', 'version': serialized_version.data})
        else:
            return Response({'message': 'Failed to update model', 'detail': serialized_version.errors}, status=status.HTTP_400_BAD_REQUEST)

# /model/model_id/version/version_id/variables
@api_view(['GET'])
def variables_view(req, model_id, version_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
        fairmodel_version = FairmodelVersion.objects.get(pk=version_id)
    except Fairmodel.DoesNotExist or FairmodelVersion.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)

    if not req.user.is_authenticated or not req.user.id == fairmodel.user.id or not fairmodel_version.fairmodel.id == model_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if not fairmodel_version.metadata_input_variables or not fairmodel_version.metadata_output_variables:
        return Response({'message': 'This version has no metadata connected to it yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not fairmodel_version.model_input_variables or not fairmodel_version.model_output_variables:
        return Response({'message': 'This version has no model connected to it yet'}, status=status.HTTP_400_BAD_REQUEST)

    vars = {
        'input': {
            'metadata': fairmodel_version.metadata_input_variables,
            'model': fairmodel_version.model_input_variables
        },
        'output': {
            'metadata': fairmodel_version.metadata_output_variables,
            'model': fairmodel_version.model_output_variables
        },
    }
    
    return Response({'variables': vars}, status=status.HTTP_400_BAD_REQUEST)

def get_variables_from_model(path: str, type: str):
    if type == 'PMML':
        raise Exception('Parsing of PMML-models is not yet supported.')
    elif type == 'ONNX':
        import onnx
        from google.protobuf.json_format import MessageToDict

        print('READING PATH:', path)
        try:
            onnx_model = onnx.load(path)
        except Exception as e:
            raise Exception("Unable to parse variables from ONNX-model")
        
        def map_onnx_vars(var):
            return {
                'name': var.name,
                'type': MessageToDict(var.type)
            }

        variables = {
            'inputs': list(map(map_onnx_vars, onnx_model.graph.input)),
            'outputs': list(map(map_onnx_vars, onnx_model.graph.output)),
        }

        return variables
    else:
        raise Exception("Unrecognized model-type")

# /model/model_id/version/version_id/model
@api_view(['GET', 'POST'])
def model_view(req, model_id, version_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
        fairmodel_version = FairmodelVersion.objects.get(pk=version_id)
    except Fairmodel.DoesNotExist or FairmodelVersion.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)

    if not req.user.is_authenticated or not req.user.id == fairmodel.user.id or not fairmodel_version.fairmodel.id == model_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    output_path = Path('storage/' + str(fairmodel.id) + '/' + str(fairmodel_version.id))

    if req.method == "GET":
        if fairmodel_version.has_model:
            f = open(output_path, 'rb')
            return FileResponse(f)
        else:
            return Response({'message': 'No model has been uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
    if req.method == "POST":
        if fairmodel_version.has_model:
            return Response({'message': 'This version already has a model'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serialized_version = FairmodelVersionSerializer(fairmodel_version, data={'model_type': req.data['model_type']}, partial=True)
            if serialized_version.is_valid():
                serialized_version.save()

                uploaded_file = req.data['file']
                output_path.parent.mkdir(exist_ok=True, parents=True)
                for c in uploaded_file.chunks():
                    output_path.write_bytes(c)

                try:
                    variables_model = get_variables_from_model(output_path, req.data['model_type'])
                except Exception as e:
                    output_path.unlink()
                    return Response({'message': 'Error parsing the variables from the model: ' + getattr(e, 'message', str(e))}, status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                update_vars_serializer = FairmodelVersionSerializer(fairmodel_version, data={
                    'model_input_variables': variables_model['inputs'],
                    'model_output_variables': variables_model['outputs']
                }, partial=True)

                if update_vars_serializer.is_valid():
                    update_vars_serializer.save()
                else:
                    print("ERROR ON SAVE:")
                    print(update_vars_serializer.errors)
                    print(variables_model['inputs'])
                    Response({'message': 'Failed to store model variables', 'detail': update_vars_serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
                
                return Response({'message': 'Uploaded successfully'}, status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Failed to update model', 'detail': serialized_version.errors}, status=status.HTTP_400_BAD_REQUEST)

# /model/model_id/version/version_id/link
@api_view(['GET', 'PUT'])
def link_view(req, model_id, version_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
        fairmodel_version = FairmodelVersion.objects.get(pk=version_id)
    except Fairmodel.DoesNotExist or FairmodelVersion.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)

    if not req.user.is_authenticated or not req.user.id == fairmodel.user.id or not fairmodel_version.fairmodel.id == model_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if req.method == "GET":
        return Response({'message': 'Not implemented yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    if req.method == "PUT":
        return Response({'message': 'Not implemented yet'}, status=status.HTTP_400_BAD_REQUEST)
