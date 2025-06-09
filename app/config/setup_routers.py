from fastapi import FastAPI


def setup_routers(app: FastAPI) -> None:
    """
    Configura las rutas de la aplicación FastAPI.

    Args:
        app: Instancia de FastAPI
    """
    from app.api.routes.ws_chat import router as chat_router
    from app.api.routes.http_chat import router as http_chat_router

    # Registrar los routers
    app.include_router(chat_router)
    app.include_router(http_chat_router)
