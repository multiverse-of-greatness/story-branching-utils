from src.repositories.story_data import StoryDataRepository


def run_delete_story(story_id: str):
    _ = StoryDataRepository().get(story_id)
    StoryDataRepository().delete(story_id)
