from typing import Optional
from fastapi import APIRouter, Body
from pydantic import BaseModel
from dotenv import load_dotenv
from data_manager import ModelDataLayer

router = APIRouter()

class CreateModelModel(BaseModel):
  name: str
  description: str
  onnx_model: str
  metadata_id: Optional[str] = None

class UpdateModelModel(BaseModel):
  onnx_model: Optional[str]
  metadata_id: Optional[str]
  update_type: str
  update_description: Optional[str] = None
  
@router.get("/model")
def list_models():
  ModelData = ModelDataLayer()
  models = ModelData.list()
  model_dict = {}

  for model_id in models:
    model_dict[model_id] = ModelData.read(model_id)
  
  return model_dict

@router.post("/model")
def create_model(data: CreateModelModel):
  ModelData = ModelDataLayer

  id = ModelData.create(data.name, data.description, data.onnx_model, data.metadata_id)

  return {"message": "Model succesfully created", "id": id}

@router.get("/model/{model_id}")
def read_model(model_id):
  ModelData = ModelDataLayer()
  data = ModelData.read(model_id)

  return data

@router.patch("/model/{model_id}")
def update_model(model_id, data: UpdateModelModel):
  ModelData = ModelDataLayer()
  data = ModelData.update(model_id, data.onnx_model, data.metadata_id, data.update_type, data.update_description)

  return data

@router.delete("/model/{model_id}")
def delete_model(model_id):
  ModelData = ModelDataLayer()
  ModelData.delete(model_id)

  return {"message": "Model succesfully deleted"}
