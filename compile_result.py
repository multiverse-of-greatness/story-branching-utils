import typer
from dotenv import load_dotenv

from src.compile_result.bias import core_bias_evaluation
from src.compile_result.evaluation import core_objective_evaluation
from src.compile_result.word_cloud import core_word_cloud_aggregation

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def summarize_obj_eval():
    core_objective_evaluation()


@app.command()
def generate_word_cloud():
    core_word_cloud_aggregation()


@app.command()
def check_bias():
    core_bias_evaluation()


if __name__ == "__main__":
    load_dotenv()
    app()
