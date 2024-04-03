from typing import Annotated

import typer
import uvicorn
from dotenv import load_dotenv

from src.api.core import api
from src.exporter.core import run_export_all, run_export_story
from src.importer.core import run_import_story

app = typer.Typer()


@app.command()
def start_api_server(port: Annotated[int, "Port to run the API server on"] = 8000):
    uvicorn.run(api, port=port)


@app.command()
def import_story(story_id: str):
    run_import_story(story_id)


@app.command()
def export_story(story_id: str):
    run_export_story(story_id)


@app.command()
def export_all():
    run_export_all()


if __name__ == "__main__":
    load_dotenv()
    app()
