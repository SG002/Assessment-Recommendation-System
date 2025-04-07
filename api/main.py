from fastapi import FastAPI
from pydantic import BaseModel
from recommend import Recommender

app = FastAPI()
recommender = Recommender()

class Query(BaseModel):
    text: str

@app.post("/recommend")
async def recommend_assessments(query: Query):
    return recommender.recommend(query.text)

# Run with: uvicorn main:app --reload