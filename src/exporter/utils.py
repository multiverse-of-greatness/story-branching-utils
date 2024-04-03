import ujson
from loguru import logger

from src.models.story_branch import StoryBranch
from src.models.story_chunk import StoryChunk


def export_story_branches(story_chunk: StoryChunk, choices: list[StoryBranch]):
    choices_dict = [c.to_dict() for c in choices]
    file_path = story_chunk.output_dir / "branches.json"
    with open(file_path, 'w') as file:
        ujson.dump(choices_dict, file, indent=2)
    logger.info(f"Exported branches to {file_path}")
