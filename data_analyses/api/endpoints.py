from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/")
def read_root(data:list[int]=Query()) -> dict:
    return {
        "hello_world": data
    }

