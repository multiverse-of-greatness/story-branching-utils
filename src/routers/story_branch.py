from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.container import get_story_branch_repository
from src.repositories.story_branch import StoryBranchRepository

router = APIRouter()


@router.get("/list/{chunk_id}")
async def get(chunk_id: str, repository: Annotated[StoryBranchRepository, Depends(get_story_branch_repository)]):
    try:
        branches = repository.list_branches_from(chunk_id)
        return JSONResponse(content=[b.to_dict() for b in branches])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=404)
