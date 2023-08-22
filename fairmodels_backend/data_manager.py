import os
import json
import uuid
from datetime import datetime
from fastapi import HTTPException

DATA_DIR = "local-data"

class DataManager:
  def __init__(self, entity_type):
    self.entity_type = entity_type
    self.data_dir = os.path.join(DATA_DIR, entity_type)
    os.makedirs(self.data_dir, exist_ok=True)

  def _get_file_path(self, entity_id):
    return os.path.join(self.data_dir, f"{entity_id}.json")

  def create_entity(self, name, description, onnx_model, metadata_id):
    entity_id = str(uuid.uuid4())

    data = {
      "id": entity_id,
      "name": name,
      "description": description,
      "versions": [{
        "version": "0.1.0",
        "onnx_model": onnx_model,
        "metadata_id": metadata_id,
        "update_description": None,
        "created_at": str(datetime.now())
      }]
    }

    file_path = self._get_file_path(entity_id)
    with open(file_path, "w") as file:
      json.dump(data, file)
    return entity_id

  def read_entity(self, entity_id):
    file_path = self._get_file_path(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "r") as file:
        return json.load(file)
    raise HTTPException(status_code=404, detail="Item not found")

  def update_entity(self, entity_id, onnx_model: str, metadata_id: str, update_type: str, update_description: str):
    model = self.read_entity(entity_id)
    
    new_version = list(map(int, str(model['versions'][-1]['version']).split('.')))
    if not len(new_version) == 3:
      raise Exception("Version-number not in semantic format")
    if update_type == 'major':
      new_version[0] += 1
      new_version[1] = 0
      new_version[2] = 0
    if update_type == 'minor':
      new_version[1] += 1
      new_version[2] = 0
    if update_type == 'patch':
      new_version[2] += 1

    new_version = '.'.join(map(str, new_version))

    new_model_version = {
      "version": new_version,
      "onnx_model": onnx_model or model['onnx_model'],
      "metadata_id": metadata_id or model['metadata_id'],
      "update_description": update_description,
      "created_at": str(datetime.now())
    }

    model['versions'].append(new_model_version)

    file_path = self._get_file_path(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "w") as file:
        json.dump(model, file)
    else:
      raise HTTPException(status_code=404, detail="Item not found")
    
    return {
      "message": "Updated model successfully",
      "version": new_version,
      "id": entity_id
    }

  def delete_entity(self, entity_id):
    file_path = self._get_file_path(entity_id)
    if os.path.isfile(file_path):
      os.remove(file_path)
    else:
      raise HTTPException(status_code=404, detail="Item not found")

  def list_entities(self):
    entity_ids = []
    for filename in os.listdir(self.data_dir):
      if filename.endswith(".json"):
        entity_id = os.path.splitext(filename)[0]
        entity_ids.append(entity_id)
    return entity_ids
