import uvicorn

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("server:app", host="0.0.0.0", port=3099, reload=True)