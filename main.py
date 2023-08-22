from typing import Optional
from fastapi import FastAPI, Body
from pydantic import BaseModel
import uvicorn
import orcid
from dotenv import load_dotenv
import os
from fairmodels_backend.data_manager import DataManager
# from fairmodels_backend.models import CreateModelModel, UpdateModelModel

load_dotenv()
app = FastAPI()

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

@app.get("/")
def root():
  return {"message": "Hello Client"}

@app.get("/model")
def list_models():
  ModelDataManager = DataManager("model")
  models = ModelDataManager.list_entities();
  model_dict = {}

  for model_id in models:
    model_dict[model_id] = ModelDataManager.read_entity(model_id)
  
  return model_dict

@app.post("/model")
def create_model(data: CreateModelModel):
  ModelDataManager = DataManager("model")

  id = ModelDataManager.create_entity(data.name, data.description, data.onnx_model, data.metadata_id)

  return {"message": "Model succesfully created", "id": id}

@app.get("/model/{model_id}")
def read_model(model_id):
  ModelDataManager = DataManager("model")
  data = ModelDataManager.read_entity(model_id)

  return data

@app.patch("/model/{model_id}")
def update_model(model_id, data: UpdateModelModel):
  ModelDataManager = DataManager("model")
  data = ModelDataManager.update_entity(model_id, data.onnx_model, data.metadata_id, data.update_type, data.update_description)

  return data

@app.delete("/model/{model_id}")
def delete_model(model_id):
  ModelDataManager = DataManager("model")
  ModelDataManager.delete_entity(model_id)

  return {"message": "Model succesfully deleted"}

@app.get("/auth_link")
def cli_auth():
  api = orcid.PublicAPI(os.getenv("ORCID_CLIENT_ID"), os.getenv("ORCID_CLIENT_SECRET"), sandbox=False)
  url = api.get_login_url(scope="/authenticate", redirect_uri="http://0.0.0.0:3099/redirect")

  return {"url": url}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=3099)