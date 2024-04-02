from loguru import logger

from src.config import DATA_PATH
from src.exporter.utils import export_story_branches
from src.repositories.story_branch import StoryBranchRepository
from src.repositories.story_chunk import StoryChunkRepository
from src.repositories.story_data import StoryDataRepository


def run_export_all():
    stories = StoryDataRepository().list()
    for story_data in stories:
        run_export_story(story_data.id)


def run_export_story(story_id: str):
    story_data_path = DATA_PATH / story_id
    if story_data_path.exists():
        raise FileExistsError(f"Story {story_id} already exists")

    logger.info(f"Exporting story {story_id}")
    story_data = StoryDataRepository().get(story_id)
    story_data.to_json_file()

    if story_data.start_chunk_id:
        frontiers: list[str] = [story_data.start_chunk_id]
        while frontiers:
            chunk_id = frontiers.pop(0)

            story_chunk = StoryChunkRepository().get(chunk_id)
            story_chunk.to_json_file()

            branches = StoryBranchRepository().list_branches(chunk_id)
            export_story_branches(story_chunk, branches)
            
            frontiers.extend([b.target_chunk_id for b in branches])
