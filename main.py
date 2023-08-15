from fastapi import FastAPI, Body

from fairmodels_backend.data_manager import DataManager

app = FastAPI()

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
def create_model(payload: dict = Body(...)):
    ModelDataManager = DataManager("model")
    id = ModelDataManager.create_entity(payload)

    return {"message": "Model succesfully created", "id": id}

@app.get("/model/{model_id}")
def read_model(model_id):
    ModelDataManager = DataManager("model")
    data = ModelDataManager.read_entity(model_id)

    return data

@app.patch("/model/{model_id}")
def update_model(model_id, payload: dict = Body(...)):
    ModelDataManager = DataManager("model")
    data = ModelDataManager.update_entity(model_id, payload)

    return data

@app.delete("/model/{model_id}")
def update_model(model_id):
    ModelDataManager = DataManager("model")
    ModelDataManager.delete_entity(model_id)

    return {"message": "Model succesfully deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3099)