import json

from loguru import logger

from src.databases import Neo4J
from src.models.story_data import StoryData


class StoryDataRepository(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StoryDataRepository, cls).__new__(cls)
            cls._instance._initialize()
            logger.info("StoryDataRepository instance created")
        return cls._instance

    def _initialize(self):
        self.database = Neo4J()

    def list(self) -> list[StoryData]:
        stories: list[StoryData] = []
        with self.database.driver.session() as session:
            results = session.run(
                ("MATCH (storyData:StoryData) "
                 "OPTIONAL MATCH (storyData)-[:STARTED_AT]->(storyChunk:StoryChunk) "
                 "RETURN storyData, storyChunk")
            )
            for record in results:
                story_obj = dict(record["storyData"])
                if record["storyChunk"]:
                    chunk_obj = dict(record["storyChunk"])
                    story_obj["start_chunk_id"] = str(chunk_obj["id"])
                stories.append(StoryData.from_dict(story_obj))
        return stories

    def get(self, story_id: str) -> StoryData:
        with self.database.driver.session() as session:
            result = session.run(
                ("MATCH (storyData:StoryData {id: $story_id}) "
                 "OPTIONAL MATCH (storyData)-[:STARTED_AT]->(storyChunk:StoryChunk) "
                 "RETURN storyData, storyChunk"),
                story_id=story_id
            )
            record = result.single()

            if record is None:
                raise ValueError("Story not found")
            
            story_obj = dict(record["storyData"])
            if record["storyChunk"]:
                chunk_obj = dict(record["storyChunk"])
                story_obj["start_chunk_id"] = str(chunk_obj["id"])
            return StoryData.from_dict(story_obj)
        
    def create(self, story_data: StoryData):
        with self.database.driver.session() as session:
            session.run(
                """CREATE (storyData:StoryData {id: $id, title: $title, genre: $genre, themes: $themes, 
                main_scenes: $main_scenes, main_characters: $main_characters, 
                synopsis: $synopsis, chapter_synopses: $chapter_synopses, 
                beginning: $beginning, endings: $endings, generated_by: $generated_by, approach: $approach})""",
                id=story_data.id, title=story_data.title, genre=story_data.genre, themes=story_data.themes,
                main_scenes=json.dumps([s.to_dict() for s in story_data.main_scenes]),
                main_characters=json.dumps([c.to_dict() for c in story_data.main_characters]), synopsis=story_data.synopsis,
                chapter_synopses=json.dumps([c.to_dict() for c in story_data.chapter_synopses]), beginning=story_data.beginning,
                endings=json.dumps([e.to_dict() for e in story_data.endings]), generated_by=story_data.generated_by,
                approach=story_data.approach.value
            )
        logger.info(f"StoryData {story_data.id} created")

    def link_chunk_for(self, story_data: StoryData):
        with self.database.driver.session() as session:
            session.run(
                ("MATCH (storyData:StoryData {id: $story_id}), (storyChunk:StoryChunk {id: $chunk_id}) "
                 "CREATE (storyData)-[:STARTED_AT]->(storyChunk)"),
                story_id=story_data.id, chunk_id=story_data.start_chunk_id
            )
        logger.info(f"StoryData {story_data.id} linked to chunk {story_data.start_chunk_id}")
