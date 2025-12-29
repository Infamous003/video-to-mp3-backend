from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": f"video-to-mp3 app is running"}
