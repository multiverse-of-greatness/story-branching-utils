import os
from pathlib import Path

import numpy as np
import ujson
from loguru import logger
from tqdm import tqdm
from typing_extensions import Any

from src.config import CRITERION, RESULT_PATH

EVAL_ERROR = -1.0


def core_objective_evaluation():
    path_to_stories = RESULT_PATH / "eval-outputs"
    for path_to_story in path_to_stories.iterdir():
        path_to_chunks = path_to_story / "objective-evaluation"
        scores = {c: [] for c in CRITERION}

        for chunk_id in tqdm(os.listdir(path_to_chunks)):
            path_to_chunk = path_to_chunks / chunk_id
            for path_to_json in path_to_chunk.glob("*.json"):
                criteria = path_to_json.name.split(".")[0]
                score = evaluate_score_json(path_to_json)
                if score == EVAL_ERROR:
                    # logger.warning(f"Error in {path_to_json}")
                    pass
                else:
                    scores[criteria].append(score)

        path_to_data = RESULT_PATH / "exported-data" / path_to_story.name / "data.json"
        with open(path_to_data, "r") as data_file:
            data = ujson.load(data_file)
        approach = data["approach"]

        logger.info(f"-- Story: {path_to_story.name} -- Approach: {approach} --")
        for c in CRITERION:
            if scores[c]:
                logger.info(f"{c}: {np.mean(scores[c]):.4f} ± {np.std(scores[c]):.4f}")
            else:
                logger.warning(f"{c}: No data")


def evaluate_score_json(path_to_json: Path) -> float:
    with open(path_to_json, "r") as json_file:
        content = ujson.load(json_file)
    parsed_output: dict = content["parsed_output"]
    criteria = path_to_json.name.split(".")[0]

    if criteria in parsed_output:
        data: list[dict] = parsed_output[criteria]
        return sum([d["score"] for d in data if validate_score(d["score"])]) / len(data)
    
    return EVAL_ERROR


def validate_score(score: Any) -> bool:
    return isinstance(score, (int, float))
