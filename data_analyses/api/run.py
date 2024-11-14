from endpoints import app
import uvicorn

# if in prod this should be False, in dev it should be True
RELOAD = True

if __name__ == "__main__":
    uvicorn.run("endpoints:app", host="0.0.0.0", port=8000, reload=RELOAD)