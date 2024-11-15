from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],  # HTTP methods: GET, POST, PUT, etc.
    allow_headers=["*"],  # Headers like Content-Type, Authorization, etc.
)

@app.get("/api")
def read_root(data:str) -> dict:
    return {
        data: data,
    }

@app.get("/api/timeTendencies")
def time_tendencies(data:List[str] = Query()) -> list[dict]:
    print(data)
    
    response = [
            { "date": "2026", "lines": {"soccer": 25, "shootiing": 17 } },
            { "date": "2025", "lines": { "tennis": 20, "soccer": 10, "shootiing": 17 } },
            { "date": "2024", "lines": { "tennis": 25, "soccer": 30, "shootiing": 17 } },
            { "date": "2021", "lines": { "tennis": 10, "soccer": 20} },
            ];
    
    return response