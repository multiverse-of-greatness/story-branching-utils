import ujson
from loguru import logger

from src.databases import Neo4J
from src.models.story_chunk import StoryChunk


class StoryChunkRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StoryChunkRepository, cls).__new__(cls)
            cls._instance._initialize()
            logger.info("StoryChunkRepository instance created")
        return cls._instance

    def _initialize(self):
        self.database = Neo4J()

    def get(self, chunk_id: str) -> StoryChunk:
        with self.database.driver.session() as session:
            result = session.run("MATCH (chunk:StoryChunk {id: $chunk_id}) RETURN chunk", chunk_id=chunk_id)
            record = result.single()

            if record is None:
                raise ValueError("Chunk not found")
            
            chunk_obj = dict(record["chunk"])
            return StoryChunk.from_dict(chunk_obj)
        
    def create(self, story_chunk: StoryChunk):
        with self.database.driver.session() as session:
            session.run(
                ("MERGE (storyChunk:StoryChunk {id: $id, chapter: $chapter, story_so_far: $story_so_far, "
                 "story: $story, history: $history, story_id: $story_id, num_opportunities: $num_opportunities})"),
                id=story_chunk.id,
                chapter=story_chunk.chapter,
                story_so_far=story_chunk.story_so_far,
                story=ujson.dumps([n.to_dict() for n in story_chunk.story]),
                history=story_chunk.history,
                story_id=story_chunk.story_id,
                num_opportunities=story_chunk.num_opportunities,
            )
        logger.info(f"StoryChunk {story_chunk.id} created")
