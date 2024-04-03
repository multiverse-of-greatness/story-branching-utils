from pathlib import Path

import ujson
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
    story_data, start_chunk_id = load_story_data_with_start_chunk_id(story_data_path)
    StoryDataRepository().create(story_data)

    if start_chunk_id:
        branches: dict[str, StoryBranch] = {}
        frontiers: list[str] = [start_chunk_id]
        while frontiers:
            chunk_id = frontiers.pop()

            story_chunk_path = story_data_path / "chunks" / chunk_id
            story_chunk, new_branches = load_story_chunk_with_branches(story_chunk_path)
            StoryChunkRepository().create(story_chunk)

            if chunk_id in branches:
                branch = branches[chunk_id]
                StoryBranchRepository().create(branch)
                del branches[chunk_id]

            for branch in new_branches:
                branches[branch.target_chunk_id] = branch
            frontiers.extend([b.target_chunk_id for b in new_branches])
        
        StoryDataRepository().link_chunk_for(story_id, start_chunk_id)


def load_story_data_with_start_chunk_id(story_data_path: Path) -> tuple[StoryData, str]:
    story_file_path = story_data_path / "data.json"
    with open(story_file_path, 'r') as file:
        story_obj = ujson.load(file)
    story_data = StoryData.from_dict(story_obj)
    start_chunk_id = story_obj["start_chunk_id"]
    return story_data, start_chunk_id


def load_story_chunk_with_branches(chunk_data_path: Path) -> tuple[StoryChunk, list[StoryBranch]]:
    chunk_file_path = chunk_data_path / "data.json"
    branches_file_path = chunk_data_path / "branches.json"
    with open(chunk_file_path, 'r') as file:
        chunk_obj = ujson.load(file)
    with open(branches_file_path, 'r') as file:
        branches = [StoryBranch.from_dict(b) for b in ujson.load(file)]
    return StoryChunk.from_dict(chunk_obj), branches
