from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import routers as r

load_dotenv()
app = FastAPI()

app.include_router(r.auth.router)
app.include_router(r.model.router)

@app.get("/")
def root():
  return {"message": "Root"}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=3099)