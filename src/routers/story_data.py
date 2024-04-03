from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.container import get_story_data_repository
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
        return JSONResponse(content={"error": str(e)}, status_code=404)
