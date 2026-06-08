from fastapi import FastAPI

app = FastAPI(title="iVibey API", version="1.0.0")

@app.get("/")
def health_check():
    return {"message": "iVibey API is running!"}