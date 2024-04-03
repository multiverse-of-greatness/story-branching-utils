from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.container import get_story_data_repository
from src.models.story_data import StoryData
from src.repositories.story_data import StoryDataRepository

router = APIRouter()


@router.get("/list")
async def list(repository: Annotated[StoryDataRepository, Depends(get_story_data_repository)], with_image: bool = False):
    stories = repository.list()
    return JSONResponse(content=[s.to_dict(with_image) for s in stories])


@router.get("/{story_id}")
async def get(story_id: str, repository: Annotated[StoryDataRepository, Depends(get_story_data_repository)], with_image: bool = False):
    try:
        story_data = repository.get(story_id)
        return JSONResponse(content=story_data.to_dict(with_image))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/")
async def create(story_data: StoryData, repository: Annotated[StoryDataRepository, Depends(get_story_data_repository)]):
    try:
        repository.create(story_data)
        return JSONResponse(content={"message": "Story data created successfully"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    

@router.put("/{story_id}/to/{chunk_id}")
async def link_chunk_for(story_id: str, chunk_id: str, repository: Annotated[StoryDataRepository, Depends(get_story_data_repository)]):
    try:
        repository.link_chunk_for(story_id, chunk_id)
        return JSONResponse(content={"message": f"Story data {story_id} linked to chunk {chunk_id}"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
