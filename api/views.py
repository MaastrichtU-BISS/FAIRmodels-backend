from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Fairmodel, FairmodelVersion
from .serializers import FairmodelSerializer, FairmodelVersionSerializer

# /
@api_view(['GET'])
def index(req):
    return Response({"Hello": "World"})

# /model
@api_view(['GET', 'POST'])
def models_view(req):
    if req.method == 'GET':
        fairmodel = Fairmodel.objects.all()
        serialized = FairmodelSerializer(fairmodel, many=True)
        return Response({'fairmodels': serialized.data})
    elif req.method == 'POST':
        if not req.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        req.data['user'] = req.user.id
        serialized = FairmodelSerializer(data=req.data, context={ 'request': req})
        if serialized.is_valid():
            created = serialized.save()
            return Response({'message': "Successfully created", 'id': created.id})
        else:
            return Response({'message': 'Failed to create model', 'detail': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)

# /model/id
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
        return Response({'fairmodelversions': serialized.data})
    
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
            created = serialized.save()
            return Response({'message': "Successfully created", 'id': created.id})
        else:
            return Response({'message': 'Failed to create model', 'detail': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
def modelversion_view(req, model_id, version_id):
    if req.method == "GET":
        pass
    elif req.method == "GET":
        pass