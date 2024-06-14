from pathlib import Path

from loguru import logger
from rich.progress import track

from src.config import OUTPUTS_PATH


def core_bias_evaluation():
    positive_word_list_path = Path("words") / "positive-words.txt"
    positive_word_list = positive_word_list_path.read_text().splitlines()
    negative_word_list_path = Path("words") / "negative-words.txt"
    negative_word_list = negative_word_list_path.read_text().splitlines()

    Path("outputs").mkdir(exist_ok=True)

    results = {
        "baseline": {
            "positive": 0,
            "negative": 0,
            "total": 0
        },
        "proposed": {
            "positive": 0,
            "negative": 0,
            "total": 0
        }
    }

    narrative_texts = [None, None]
    path_to_stories = [OUTPUTS_PATH / 'all-text-baseline.txt', OUTPUTS_PATH / 'all-text-proposed.txt']
    for idx, path in enumerate(path_to_stories):
        narrative_texts[idx] = path.read_text().split(" ")

    for idx, narrative_text in enumerate(narrative_texts):
        logger.info(f"Processing {path_to_stories[idx]}")
        positive_count = 0
        negative_count = 0
        total_count = 0

        for word in track(narrative_text):
            if word in positive_word_list:
                positive_count += 1
            elif word in negative_word_list:
                negative_count += 1
            total_count += 1

        results["baseline" if idx == 0 else "proposed"]["positive"] = positive_count
        results["baseline" if idx == 0 else "proposed"]["negative"] = negative_count
        results["baseline" if idx == 0 else "proposed"]["total"] = total_count

        logger.info(f"Positive words count: {positive_count}")
        logger.info(f"Negative words count: {negative_count}")
        logger.info(f"Total words count: {total_count}")

    bias_result_path = OUTPUTS_PATH / "bias_result.csv"
    with bias_result_path.open("w") as f:
        f.write("model,positive,negative,total\n")
        f.write(f"baseline,{results['baseline']['positive']},{results['baseline']['negative']}," +
                f"{results['baseline']['total']}\n")
        f.write(f"proposed,{results['proposed']['positive']},{results['proposed']['negative']}," +
                f"{results['proposed']['total']}\n")
    logger.info(f"Results saved to {bias_result_path}")
