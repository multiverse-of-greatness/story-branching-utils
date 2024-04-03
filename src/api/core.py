from fastapi import FastAPI

import src.api.routers.story_branch as story_branch_router
import src.api.routers.story_chunk as story_chunk_router
import src.api.routers.story_data as story_data_router

api = FastAPI()


api.include_router(
    story_branch_router.router, 
    prefix="/api/v1/story-branch",
    tags=["StoryBranch"]
)

api.include_router(
    story_chunk_router.router, 
    prefix="/api/v1/story-chunk",
    tags=["StoryChunk"]
)

api.include_router(
    story_data_router.router, 
    prefix="/api/v1/story-data",
    tags=["StoryData"]
)
