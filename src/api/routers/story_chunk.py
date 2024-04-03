from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.container import get_story_chunk_repository
from src.models.story_chunk import StoryChunk
from src.repositories.story_chunk import StoryChunkRepository

router = APIRouter()


@router.get("/{chunk_id}")
async def get(chunk_id: str, repository: Annotated[StoryChunkRepository, Depends(get_story_chunk_repository)], with_history: bool = False):
    try:
        chunk = repository.get(chunk_id)
        return JSONResponse(content=chunk.to_dict(with_history))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/")
async def create(story_chunk: StoryChunk, repository: Annotated[StoryChunkRepository, Depends(get_story_chunk_repository)]):
    try:
        repository.create(story_chunk)
        return JSONResponse(content={"message": "Story chunk created successfully"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
