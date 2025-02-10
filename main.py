from fastapi import FastAPI
from routers.containers import router as containers_router
import docker

client = docker.from_env()

app = FastAPI()

# Include the containers router
app.include_router(containers_router, prefix="/api", tags=["containers"])

@app.get("/")
async def root():
    print("LIst containers",client.containers.list())
    return {"message": "Welcome to the Container Management API!"}
