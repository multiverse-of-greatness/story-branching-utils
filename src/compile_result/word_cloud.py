import os
from pathlib import Path

import ujson
from tqdm import tqdm
from wordcloud import WordCloud

from src.compile_result.utils import clean
from src.config import OUTPUTS_PATH, RESULT_PATH
from src.models.enums.generation_approach import GenerationApproach


def core_word_cloud_aggregation():
    Path("outputs").mkdir(exist_ok=True)

    narrative_texts = ["", ""]
    path_to_stories = RESULT_PATH / "exported-data"
    for path_to_story in path_to_stories.iterdir():
        with open(path_to_story / "data.json", "r") as data_file:
            story_data = ujson.load(data_file)
        approach = story_data["approach"]
        approach_idx = int(approach == GenerationApproach.PROPOSED)

        path_to_chunks = path_to_story / "chunks"
        for chunk_id in tqdm(os.listdir(path_to_chunks)):
            path_to_chunk = path_to_chunks / chunk_id
            narrative_texts[approach_idx] += process_story_narratives(path_to_chunk / "data.json") + " "
    
    for approach in GenerationApproach:
        approach_idx = int(approach == GenerationApproach.PROPOSED)
        wc = WordCloud(
            width=1600, height=1000,
            background_color="white",
            collocations=False,
            random_state=42,
        )
        wc.generate(narrative_texts[approach_idx].strip())
        wc.to_file(OUTPUTS_PATH / f"wordcloud-{approach.value}.png")


def process_story_narratives(path_to_json: Path) -> str:
    narrative_text = ""
    with open(path_to_json, "r") as file:
        content = ujson.load(file)
    for story in content["story"]:
        narrative_text += clean(story["text"])
    return narrative_text
