import typer
from dotenv import load_dotenv

from src.compile_result.step1 import core_objective_evaluation

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def run_step_1():
    core_objective_evaluation()


@app.command()
def run_step_2():
    typer.echo(f"Step 2")


if __name__ == "__main__":
    load_dotenv()
    app()
