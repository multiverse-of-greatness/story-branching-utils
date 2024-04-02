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

    def list_branches(self, chunk_id: str) -> list[StoryBranch]:
        branches = []
        with self.database.driver.session() as session:
            query = "MATCH (source:StoryChunk {id: $chunk_id})-[b:BRANCHED_TO]->(target:StoryChunk) RETURN source, target, PROPERTIES(b)"
            results = session.run(query, chunk_id=chunk_id)

            for record in results:
                source_chunk_obj = dict(record["source"])
                target_chunk_obj = dict(record["target"])
                choice_obj = dict(record["PROPERTIES(b)"])
                branch_obj = {
                    "source_chunk_id": source_chunk_obj["id"],
                    "target_chunk_id": target_chunk_obj["id"],
                    "choice": choice_obj,
                }
                branches.append(StoryBranch.from_dict(branch_obj))

        return branches
    
    def create(self, branch: StoryBranch):
        with self.database.driver.session() as session:
            session.run(
                ("MATCH (source:StoryChunk {id: $source_id}), (branched:StoryChunk {id: $branched_id}) "
                 "CREATE (source)-[:BRANCHED_TO $props]->(branched)"),
                source_id=branch.source_chunk_id,
                branched_id=branch.target_chunk_id,
                props={} if not branch.choice else branch.choice.to_dict(),
            )
        logger.info(f"Created branch from {branch.source_chunk_id} to {branch.target_chunk_id}")
