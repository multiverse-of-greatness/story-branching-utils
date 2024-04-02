import typer
from dotenv import load_dotenv

from src.core import run_delete_story
from src.exporter.core import run_export_all, run_export_story
from src.importer.core import run_import_story

app = typer.Typer()


@app.command()
def export_story(story_id: str):
    run_export_story(story_id)


@app.command()
def export_all():
    run_export_all()


@app.command()
def import_story(story_id: str):
    run_import_story(story_id)


@app.command()
def delete_story(story_id: str):
    run_delete_story(story_id)


if __name__ == "__main__":
    load_dotenv()
    app()
