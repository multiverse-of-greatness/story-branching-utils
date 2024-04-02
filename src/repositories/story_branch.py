import ujson
from loguru import logger

from src.databases import Neo4J
from src.models.story_branch import StoryBranch


class StoryBranchRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StoryBranchRepository, cls).__new__(cls)
            cls._instance._initialize()
            logger.info("StoryBranchRepository instance created")
        return cls._instance

    def _initialize(self):
        self.database = Neo4J()

    def list_branches_from(self, chunk_id: str) -> list[StoryBranch]:
        branches = []
        with self.database.driver.session() as session:
            query = "MATCH (source:StoryChunk {id: $chunk_id})-[b:BRANCHED_TO]->(target:StoryChunk) RETURN source, target, PROPERTIES(b)"
            results = session.run(query, chunk_id=chunk_id)

            for record in results:
                source_chunk_obj = dict(record["source"])
                target_chunk_obj = dict(record["target"])
                branch_obj = dict(record["PROPERTIES(b)"])
                branch_obj["source_chunk_id"] = source_chunk_obj["id"]
                branch_obj["target_chunk_id"] = target_chunk_obj["id"]
                branches.append(StoryBranch.from_dict(branch_obj))

        return branches
    
    def create(self, branch: StoryBranch):
        with self.database.driver.session() as session:
            session.run(
                ("MATCH (source:StoryChunk {id: $source_id}), (branched:StoryChunk {id: $branched_id}) "
                 "MERGE (source)-[:BRANCHED_TO {choice: $choice}]->(branched)"),
                source_id=branch.source_chunk_id,
                branched_id=branch.target_chunk_id,
                choice='{}' if branch.choice is None else ujson.dumps(branch.choice.to_dict()),
            )
        logger.info(f"Created branch from {branch.source_chunk_id} to {branch.target_chunk_id}")
