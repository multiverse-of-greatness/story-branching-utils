import os
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import nltk
import seaborn as sns
import ujson
from loguru import logger
from nltk.tokenize.toktok import ToktokTokenizer
from tqdm import tqdm
from wordcloud import WordCloud

from src.config import OUTPUTS_PATH, RESULT_PATH
from src.models.enums.generation_approach import GenerationApproach


def core_word_cloud_aggregation():
    nltk.download('wordnet')
    nltk.download('stopwords')

    Path("outputs").mkdir(exist_ok=True)

    narrative_texts = ["", ""]
    path_to_stories = RESULT_PATH / "exported-data"
    stories = [story for story in os.listdir(path_to_stories) if os.path.isdir(path_to_stories / story)]
    for story_id in tqdm(stories):
        path_to_story = path_to_stories / story_id
        with open(path_to_story / "data.json", "r") as data_file:
            story_data = ujson.load(data_file)
        approach = story_data["approach"]
        approach_idx = int(approach == GenerationApproach.PROPOSED)

        path_to_chunks = path_to_story / "chunks"
        for path_to_chunk in path_to_chunks.iterdir():
            narrative_texts[approach_idx] += process_story_narratives(path_to_chunk / "data.json") + " "

    for approach in GenerationApproach:
        logger.info(f"Generating word cloud for {approach.value} approach")
        approach_idx = int(approach == GenerationApproach.PROPOSED)
        wc = WordCloud(
            width=1200, height=750,
            background_color="white",
            collocations=False,
            min_word_length=2,
            random_state=42,

        )

        text = narrative_texts[approach_idx].strip().split(' , ')
        text = [item.strip() for sublist in text for item in sublist.split()]

        lemmatizer = nltk.WordNetLemmatizer()
        text = [lemmatizer.lemmatize(word) for word in text]

        stop_words = set(nltk.corpus.stopwords.words("english"))
        text = [word for word in text if word not in stop_words and word.isalnum()]

        text = [word for word in text if len(word) > 1]

        text = " ".join(text)

        wc.generate(text)
        wc.to_file(OUTPUTS_PATH / f"wordcloud-{approach.value}.png")

        word_freq = Counter(text.split())
        word_freq = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:30])
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(20, 10))
        sns.set(font_scale=1.5)
        sns.barplot(x=list(word_freq.keys()), y=list(word_freq.values()))
        plt.xticks(rotation=90)
        plt.title(f"Top 30 frequent words for {approach.value} approach")
        plt.savefig(OUTPUTS_PATH / f"word_freq_barplot-{approach.value}.png", bbox_inches='tight')

        with open(OUTPUTS_PATH / f"all-text-{approach.value}.txt", "w") as file:
            file.write(text)


def process_story_narratives(path_to_json: Path) -> str:
    narrative_text = ""
    with open(path_to_json, "r") as file:
        content = ujson.load(file)
    for story in content["story"]:
        narrative_text += tokenize(story["text"]) + " "
    return narrative_text


def tokenize(string: str) -> str:
    tokenizer = ToktokTokenizer()
    string = tokenizer.tokenize(string, return_str=True)
    return string.lower()
