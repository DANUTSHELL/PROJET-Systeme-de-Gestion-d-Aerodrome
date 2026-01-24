from fastapi import FastAPI

from CRUD import RequeteSQL

Aerodrome = RequeteSQL("Aerodrome.db")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}