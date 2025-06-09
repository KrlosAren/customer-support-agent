from fastapi import FastAPI

def setup_routers(app: FastAPI) -> None:
    """
    Configura las rutas de la aplicación FastAPI.

    Args:
        app: Instancia de FastAPI
    """
    from app.api.routes.chat import router as chat_router

    # Registrar los routers
    app.include_router(chat_router)

