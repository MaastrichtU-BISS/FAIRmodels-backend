import os
import json
import uuid
from fastapi import HTTPException

DATA_DIR = "local-data"

class DataManager:
  def __init__(self, entity_type):
    self.entity_type = entity_type
    self.data_dir = os.path.join(DATA_DIR, entity_type)
    os.makedirs(self.data_dir, exist_ok=True)

  def _get_file_path(self, entity_id):
    return os.path.join(self.data_dir, f"{entity_id}.json")

  def create_entity(self, data, entity_id=None):
    if entity_id is None:
        entity_id = str(uuid.uuid4())

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

  def update_entity(self, entity_id, onnx_model: str, update_type: str, update_description: str):
    data = {
      onnx_model: onnx_model,
      # version: '0.2.0', #     <-- TODO: version should be updated based on update_type. 
      update_description: update_description
    }

    file_path = self._get_file_path(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "w") as file:
        json.dump(data, file)
    else:
      raise HTTPException(status_code=404, detail="Item not found")

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
