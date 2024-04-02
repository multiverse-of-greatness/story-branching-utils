import json

from loguru import logger

from src.config import DATA_PATH
from src.models.story_branch import StoryBranch
from src.models.story_chunk import StoryChunk
from src.models.story_data import StoryData
from src.repositories.story_branch import StoryBranchRepository
from src.repositories.story_chunk import StoryChunkRepository
from src.repositories.story_data import StoryDataRepository


def run_import_story(story_id: str):
    story_data_path = DATA_PATH / story_id
    if not story_data_path.exists():
        raise FileNotFoundError(f"Story data not found at {story_data_path}")
    
    logger.info(f"Importing story data from {story_data_path}")
    story_data = StoryData.from_json_file(story_data_path / "data.json")
    StoryDataRepository().create(story_data)

    if story_data.start_chunk_id:
        branches: list[StoryBranch] = []
        frontiers: list[str] = [story_data.start_chunk_id]
        while frontiers:
            chunk_id = frontiers.pop()

            chunk_path = story_data_path / "chunks" / chunk_id
            story_chunk = StoryChunk.from_json_file(chunk_path / "data.json")
            StoryChunkRepository().create(story_chunk)

            with open(chunk_path / "branches.json", 'r') as file:
                new_branches = [StoryBranch.from_dict(b) for b in json.load(file)]

            branches.extend(new_branches)
            frontiers.extend([b.target_chunk_id for b in new_branches])
        
        StoryDataRepository().link_chunk_for(story_data)
        for branch in branches:
            StoryBranchRepository().create(branch)
