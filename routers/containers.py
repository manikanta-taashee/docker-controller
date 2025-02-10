from fastapi import APIRouter, HTTPException
from services.docker_service import create_container, get_container, remove_container, list_containers

router = APIRouter()

@router.post("/create-container/")
async def create_container_endpoint(username: str):
    try:
        result = create_container(username)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create container: {str(e)}")

@router.get("/get-container/{container_name}")
async def get_container_endpoint(container_name: str):
    try:
        result = get_container(container_name)
        if not result:
            raise HTTPException(status_code=404, detail="Container not found.")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve container: {str(e)}")

@router.delete("/remove-container/{container_name}")
async def remove_container_endpoint(container_name: str):
    try:
        result = remove_container(container_name)
        if not result:
            raise HTTPException(status_code=404, detail="Container not found.")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove container: {str(e)}")

@router.get("/list-containers/")
async def list_containers_endpoint():
    try:
        return list_containers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list containers: {str(e)}")
