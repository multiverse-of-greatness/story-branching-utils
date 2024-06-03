import os
from pathlib import Path

import ujson
from loguru import logger
from tqdm import tqdm

from src.config import RESULT_PATH
from src.models.enums.generation_approach import GenerationApproach

EVAL_ERROR = -1.0


def core_word_cloud_aggregation():
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/step-2.log")

    word_cloud_per_approach = [{}, {}]

    path_to_stories = RESULT_PATH / "exported-data"
    for path_to_story in path_to_stories.iterdir():
        with open(path_to_story / "data.json", "r") as data_file:
            story_data = ujson.load(data_file)
        approach = story_data["approach"]
        approach_idx = int(approach == GenerationApproach.PROPOSED)

        path_to_chunks = path_to_story / "chunks"
        for chunk_id in tqdm(os.listdir(path_to_chunks)):
            path_to_chunk = path_to_chunks / chunk_id
            word_cloud = process_story_narratives(path_to_chunk / "data.json")
            for word, count in word_cloud.items():
                word_cloud_per_approach[approach_idx][word] = word_cloud_per_approach[approach_idx].get(word, 0) + count

        logger.info(word_cloud_per_approach)


def process_story_narratives(path_to_json: Path) -> dict:
    word_cloud = dict()
    with open(path_to_json, "r") as file:
        content = ujson.load(file)
    narratives: list = content["story"]
    for story in narratives:
        narrative_text: str = story["text"]
        for word in narrative_text.split(' '):
            word = process_word(word)
            word_cloud[word] = word_cloud.get(word, 0) + 1
    return word_cloud


def process_word(word: str) -> str:
    trim_chars = ['.', ',', '!', '?', '(', ')']
    for char in trim_chars:
        word = word.replace(char, '')
    return word.lower()
