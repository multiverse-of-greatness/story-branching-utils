import typer
from dotenv import load_dotenv

from src.compile_result.step1 import core_objective_evaluation
from src.compile_result.step2 import core_word_cloud_aggregation

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def run_step_1():
    core_objective_evaluation()


@app.command()
def run_step_2():
    core_word_cloud_aggregation()


if __name__ == "__main__":
    load_dotenv()
    app()
