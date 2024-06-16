import os
from pathlib import Path

import numpy as np
import pandas as pd
import ujson
from loguru import logger
from rich.progress import track
from typing_extensions import Any

from src.config import CRITERION, RESULT_PATH, OUTPUTS_PATH
from src.models.enums.generation_approach import GenerationApproach

EVAL_ERROR = -1.0


def core_objective_evaluation():
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/step-1.log")

    best_score_per_approach = [0.0, 0.0]
    best_story_id_per_approach = ["", ""]

    SKIPPED_STORY_IDS = ["714eeff3-03ab-11ef-bd4b-182649966cd4", "c7783c18-f70b-11ee-ac52-182649966cd4"]

    path_to_stories = RESULT_PATH / "eval-outputs"
    stories = [p for p in path_to_stories.iterdir() if p.is_dir() and p.name not in SKIPPED_STORY_IDS]

    results = {
        "baseline": [],
        "proposed": []
    }

    for path_to_story in track(stories):
        logger.info(f"Processing {path_to_story.name}")
        path_to_chunks = path_to_story / "objective-evaluation"
        scores = {c: [] for c in CRITERION}

        for chunk_id in track(os.listdir(path_to_chunks)):
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

        title = data['title']
        synopsis = data['synopsis']
        approach = data["approach"]

        logger.info(f"-- Story: {path_to_story.name} -- Approach: {approach} --")
        for c in CRITERION:
            if scores[c]:
                logger.info(f"{c}: {np.mean(scores[c]):.4f} ± {np.std(scores[c]):.4f}")
            else:
                logger.warning(f"{c}: No data")

        avg_score = np.mean([np.mean(scores[c]) for c in CRITERION if scores[c]])
        std_score = np.std([np.mean(scores[c]) for c in CRITERION if scores[c]])
        logger.info(f"Average: {avg_score:.4f}")

        summarized_scores = {c: {
            "mean": np.mean(scores[c]),
            "std": np.std(scores[c]),
        } for c in CRITERION}

        results[approach].append({
            "title": title,
            "synopsis": synopsis,
            "story_id": path_to_story.name,
            "avg_score": avg_score,
            "std_score": std_score,
            "raw_scores": summarized_scores,
        })

        if approach == GenerationApproach.BASELINE and avg_score > best_score_per_approach[0]:
            best_story_id_per_approach[0] = path_to_story.name
            best_score_per_approach[0] = avg_score
        elif approach == GenerationApproach.PROPOSED and avg_score > best_score_per_approach[1]:
            best_story_id_per_approach[1] = path_to_story.name
            best_score_per_approach[1] = avg_score

    logger.info(f"Best story id for baseline: {best_story_id_per_approach[0]}")
    logger.info(f"Best story id for proposed: {best_story_id_per_approach[1]}")
    logger.info(f"Best score for baseline: {best_score_per_approach[0]:.4f}")
    logger.info(f"Best score for proposed: {best_score_per_approach[1]:.4f}")

    logger.info(f"Average scores for baseline: {np.mean([r['avg_score'] for r in results['baseline']]):.4f}")
    logger.info(f"Average scores for proposed: {np.mean([r['avg_score'] for r in results['proposed']]):.4f}")

    data = []

    for approach in ["baseline", "proposed"]:
        for result in results[approach]:
            row = {
                "story_id": result["story_id"],
                "title": result["title"],
                "synopsis": result["synopsis"],
                "approach": approach,
                "avg_score": result["avg_score"],
                "std_score": result["std_score"],
            }
            row.update({f"avg_{c.lower().replace(' ', '_')}": result["raw_scores"][c]["mean"] for c in CRITERION})
            row.update({f"std_{c.lower().replace(' ', '_')}": result["raw_scores"][c]["std"] for c in CRITERION})
            data.append(row)

    df = pd.DataFrame(data)

    path_to_results = OUTPUTS_PATH / "objective-evaluation-results.csv"
    df.to_csv(path_to_results, index=False)

    logger.info(f"Results saved to {path_to_results}")


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
