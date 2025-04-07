import os
import google.generativeai as genai
import pandas as pd
import numpy as np
import faiss
from dotenv import load_dotenv

load_dotenv()

def generate_embeddings():
    df = pd.read_csv("data/shl_assessments.csv")
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    
    # Generate embeddings for assessment names/descriptions
    df["embedding"] = df["name"].apply(
        lambda x: genai.embed_content(model="models/embedding-001", content=x)["embedding"]
    )
    
    # Save embeddings to FAISS index
    embeddings = np.array(df["embedding"].tolist()).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, "data/assessments.index")
    df.to_csv("data/assessments_with_embeddings.csv", index=False)

if __name__ == "__main__":
    generate_embeddings()