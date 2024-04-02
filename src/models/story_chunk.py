from dataclasses import dataclass
from pathlib import Path

import ujson
from loguru import logger

from src.config import DATA_PATH
from src.models.story.story_narrative import StoryNarrative


@dataclass
class StoryChunk:
    id: str
    story_id: str
    chapter: int
    story_so_far: str
    story: list[StoryNarrative]
    num_opportunities: int
    history: str

    @property
    def output_dir(self) -> Path:
        return DATA_PATH / self.story_id / "chunks" / self.id

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "story_id": self.story_id,
            "chapter": self.chapter,
            "story_so_far": self.story_so_far,
            "story": [narrative.to_dict() for narrative in self.story],
            "num_opportunities": self.num_opportunities,
            "history": self.history,
        }

    def to_json_file(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.output_dir / "data.json"
        with open(file_path, 'w') as file:
            ujson.dump(self.to_dict(), file, indent=2)
        logger.info(f"Exported story chunk to {file_path}")

    @classmethod
    def from_dict(cls, data_obj: dict):
        if isinstance(data_obj.get("story"), str):
            data_obj["story"] = ujson.loads(data_obj.get("story"))
        return cls(
            id=data_obj.get("id"),
            story_id=data_obj.get("story_id"),
            chapter=data_obj.get("chapter"),
            story_so_far=data_obj.get("story_so_far"),
            story=[StoryNarrative.from_dict(n) for n in data_obj.get("story", [])],
            num_opportunities=data_obj.get("num_opportunities"),
            history=data_obj.get("history"),
        )
    
    @classmethod
    def from_json_file(cls, file_path: Path):
        with open(file_path, 'r') as file:
            return cls.from_dict(ujson.load(file))
    
    def get_narratives(self) -> str:
        return '\n'.join([f"{narrative.speaker}: {narrative.text}" for narrative in self.story])

    def __str__(self):
        return (f"StoryChunk(id={self.id}, story_id={self.story_id}, chapter={self.chapter}, story_so_far={self.story_so_far}, "
                f"story={[str(n) for n in self.story]}, num_opportunities={self.num_opportunities})")
    
    def __repr__(self):
        return str(self)
