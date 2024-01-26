from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
from .models import Fairmodel, FairmodelVersion
from .serializers import FairmodelSerializer, FairmodelVersionSerializer
from pathlib import Path

# /
@api_view(['GET'])
def index(req):
    return Response({"Hello": "World"})

# /model
@api_view(['GET', 'POST'])
def models_view(req):
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
def model_view(req, model_id):
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
        fairmodel_versions = FairmodelVersion.objects.filter(fairmodel=fairmodel).all()
        serialized = FairmodelVersionSerializer(fairmodel_versions, many=True)
        return Response({'fairmodelversions': map(lambda x: {'version': x, 'onnx_file': get_onnx_model(fairmodel.id, x['id'])}, serialized.data)})
    
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
        serialized = FairmodelVersionSerializer(data=req.data, context={ 'request': req})
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
        onnx_file = get_onnx_model(fairmodel.id, fairmodel_version.id)
        serialized_version = FairmodelVersionSerializer(fairmodel_version)
        return Response({'fairmodelversion': serialized_version.data, 'onnx_file': onnx_file })

    elif req.method == "PUT":
        if fairmodel_version.metadata_id:
            return Response({'message': 'This version already has "metadata_id" and cannot be updated again. Create a new version instead.'}, status=status.HTTP_400_BAD_REQUEST)
        if not req.data['metadata_id']:
            return Response({'message': 'Expected parameter: only "metadata_id"'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_version = FairmodelVersionSerializer(fairmodel_version, data={'metadata_id': req.data['metadata_id']}, partial=True)
        if serialized_version.is_valid():
            serialized_version.save()
            return Response({'message': 'Update succeded', 'version': serialized_version.data})
        else:
            return Response({'message': 'Failed to update model', 'detail': serialized_version.errors}, status=status.HTTP_400_BAD_REQUEST)

    # elif req.method == "DELETE":
    #     fairmodel_version.delete()
    #     return Response({'message': 'Deleted successfully'})

# /model/model_id/version/version_id/upload_onnx
@api_view(['GET', 'POST'])
def onnx_view(req, model_id, version_id):
    try:
        fairmodel = Fairmodel.objects.get(pk=model_id)
        fairmodel_version = FairmodelVersion.objects.get(pk=version_id)
    except Fairmodel.DoesNotExist or FairmodelVersion.DoesNotExist:
        return Response({'message': 'The given ID was not found in the database'}, status=status.HTTP_404_NOT_FOUND)

    if not req.user.is_authenticated or not req.user.id == fairmodel.user.id or not fairmodel_version.fairmodel.id == model_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if req.method == "GET":
        onnx_path = Path('storage/' + str(fairmodel.id) + '/' + str(fairmodel_version.id) + '.onnx')
        try:
            f = open(onnx_path, 'rb')
            return FileResponse(f)
        except:
            return Response({'message': 'No onnx file has been uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
    if req.method == "POST":
        output_path = Path('storage/' + str(fairmodel.id) + '/' + str(fairmodel_version.id) + '.onnx')
        try:
            f = open(output_path, 'r')
            return Response({'message': 'This version already has an onnx file'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            uploaded_file = req.data['file']
            output_path.parent.mkdir(exist_ok=True, parents=True)
            for c in uploaded_file.chunks():
                output_path.write_bytes(c)
            return Response({'message': 'Uploaded successfully'}, status.HTTP_201_CREATED)

def get_onnx_model(model_id, version_id):
    output_path = Path('storage/' + str(model_id) + '/' + str(version_id) + '.onnx')
    onnx_file = None
    try:
        with open(output_path, 'r+') as f:
            onnx_file = f.name
    except:
        pass
    return onnx_file

        

