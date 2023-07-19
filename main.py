from fastapi import FastAPI, Body

from fairmodels_backend.data_manager import DataManager

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hi World"}

@app.post("/model")
def create_model(payload: dict = Body(...)):
    ModelDataManager = DataManager("model")
    id = ModelDataManager.create_entity(payload)

    return {"message": "Model succesfully created", "id": id}

@app.get("/model/{model_id}")
def read_model(model_id):
    ModelDataManager = DataManager("model")
    data = ModelDataManager.read_entity(model_id)

    return data;

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)