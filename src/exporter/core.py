import ujson
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
        logger.warning(f"Story {story_id} already exists")
        return

    logger.info(f"Exporting story {story_id}")
    story_data, start_chunk_id = StoryDataRepository().get_with_start_chunk_id(story_id)
    story_data.output_dir.mkdir(parents=True, exist_ok=True)
    story_file_path = story_data.output_dir / "data.json"
    with open(story_file_path, 'w') as file:
        story_obj = story_data.to_dict(include_image=True)
        story_obj["start_chunk_id"] = start_chunk_id
        ujson.dump(story_obj, file, indent=2)
    logger.info(f"Exported story data to {story_file_path}")

    if start_chunk_id:
        frontiers: list[str] = [start_chunk_id]
        while frontiers:
            chunk_id = frontiers.pop(0)

            story_chunk = StoryChunkRepository().get(chunk_id)
            story_chunk.output_dir.mkdir(parents=True, exist_ok=True)
            chunk_file_path = story_chunk.output_dir / "data.json"
            with open(chunk_file_path, 'w') as file:
                chunk_obj = story_chunk.to_dict(include_history=True)
                ujson.dump(chunk_obj, file, indent=2)
            logger.info(f"Exported story chunk to {chunk_file_path}")

            branches = StoryBranchRepository().list_branches_from(chunk_id)
            export_story_branches(story_chunk, branches)
            
            frontiers.extend([b.target_chunk_id for b in branches])
