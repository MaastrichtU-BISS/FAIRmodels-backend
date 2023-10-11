from fastapi import FastAPI
from dotenv import load_dotenv
import routers as r

load_dotenv()
app = FastAPI()

app.include_router(r.auth.router)
app.include_router(r.model.router)

@app.get("/")
def root():
  return {"message": "Root"}
