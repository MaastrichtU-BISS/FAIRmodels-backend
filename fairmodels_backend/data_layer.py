import os
import json
import uuid
from datetime import datetime
from fastapi import HTTPException
from secrets import token_hex
from glob import glob
import re

DATA_DIR = "local-data"

class DataLayer:
  def __init__(self, entity_type):
    self.entity_type = entity_type
    self.data_dir = os.path.join(DATA_DIR, entity_type)
    os.makedirs(self.data_dir, exist_ok=True)

  def find_by_id(self, entity_id):
    return os.path.join(self.data_dir, f"{entity_id}.json")

class UserNotFoundException(Exception):
  pass

class UserDataLayer(DataLayer):
  def __init__(self):
    super().__init__('user')

  def find_by_username(self, username):
    for file in glob(os.path.join(DATA_DIR, 'user/*.json')):
      user_id = re.findall(r'user\/(.*?)\.json', file)[0]
      try:
        data = self.read(user_id)
        if data['username'] == username:
          return data
      except HTTPException as e:
        if (e.detail == "Item not found"):
          continue
    raise UserNotFoundException("User not found")

  def create(self, username, password_hash):
    # search_user
    try:
      self.find_by_username(username)
    except UserNotFoundException as e:
      pass
    else:
      raise HTTPException(status_code=400, detail="This username is not available")
    
    entity_id = str(uuid.uuid4())

    data = {
      "id": entity_id,
      "username": username,
      "password_hash": password_hash,
      "apikeys": []
    }

    file_path = self.find_by_id(entity_id)
    with open(file_path, "w") as file:
      json.dump(data, file)
    return entity_id

  def read(self, entity_id):
    file_path = self.find_by_id(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "r") as file:
        return json.load(file)
    raise HTTPException(status_code=404, detail="Item not found")

  def update(self, entity_id, username = None, password = None):
    entity = self.read(entity_id)

    file_path = self.find_by_id(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "w") as file:
        json.dump(entity, file)
    else:
      raise HTTPException(status_code=404, detail="Item not found")
    
    return {
      "message": "Updated user successfully",
      "id": entity_id
    }
  
  def generate_api_key(self, entity_id):
    entity = self.read(entity_id)
    
    key = token_hex(32)
    entity['apikeys'].append(key)

    file_path = self.find_by_id(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "w") as file:
        json.dump(entity, file)
    else:
      raise HTTPException(status_code=404, detail="Item not found")
    
    return {
      "key": key
    }
  
  def revoke_apikey(self, entity_id, key):
    entity = self.read(entity_id)

    entity.apikeys.remove(key)

    file_path = self.find_by_id(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "w") as file:
        json.dump(entity, file)
    else:
      raise HTTPException(status_code=404, detail="Item not found")
    
    return {
      "message": "Successfully revoked apikey"
    }

class ModelDataLayer(DataLayer):
  def __init__(self):
    super().__init__('model')

  def create(self, name, description, onnx_model, metadata_id):
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

    file_path = self.find_by_id(entity_id)
    with open(file_path, "w") as file:
      json.dump(data, file)
    return entity_id

  def read(self, entity_id):
    file_path = self.find_by_id(entity_id)
    if os.path.isfile(file_path):
      with open(file_path, "r") as file:
        return json.load(file)
    raise HTTPException(status_code=404, detail="Item not found")

  def update(self, entity_id, onnx_model: str, metadata_id: str, update_type: str, update_description: str):
    model = self.read(entity_id)
    
    new_version = list(map(int, str(model['versions'][-1]['version']).split('.')))
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
      raise Exception("Invalid update-type")

    new_version = '.'.join(map(str, new_version))

    new_model_version = {
      "version": new_version,
      "onnx_model": onnx_model or (model['onnx_model'] if 'onnx_model' in model else None),
      "metadata_id": metadata_id or (model['metadata_id'] if 'metadata_id' in model else None),
      "update_description": update_description,
      "created_at": str(datetime.now())
    }

    model['versions'].append(new_model_version)

    file_path = self.find_by_id(entity_id)
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

  def delete(self, entity_id):
    file_path = self.find_by_id(entity_id)
    if os.path.isfile(file_path):
      os.remove(file_path)
    else:
      raise HTTPException(status_code=404, detail="Item not found")

  def list(self):
    entity_ids = []
    for filename in os.listdir(self.data_dir):
      if filename.endswith(".json"):
        entity_id = os.path.splitext(filename)[0]
        entity_ids.append(entity_id)
    return entity_ids
