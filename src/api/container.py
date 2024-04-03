from src.repositories.story_branch import StoryBranchRepository
from src.repositories.story_chunk import StoryChunkRepository
from src.repositories.story_data import StoryDataRepository


def get_story_branch_repository() -> StoryBranchRepository:
    return StoryBranchRepository()


def get_story_chunk_repository() -> StoryChunkRepository:
    return StoryChunkRepository()


def get_story_data_repository() -> StoryDataRepository:
    return StoryDataRepository()
