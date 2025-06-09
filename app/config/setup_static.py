from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


def setup_static(app: FastAPI) -> None:
    """
    Setup static files for the application.
    """

    app.mount(
        "/static",
        StaticFiles(directory="app/static", html=True),
        name="static",
    )
