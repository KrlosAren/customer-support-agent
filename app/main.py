from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.config.setup_middlewares import setup_middlewares
from app.config.setup_routers import setup_routers
from app.bootstrap.bootstrap import get_bootstrap
from app.config.settings import get_settings

from app.config.setup_static import setup_static
from app.utils.logger import get_logger

logger = get_logger(name=__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app."""
    logger.info("Starting lifespan context manager")
    bootstrap = get_bootstrap(settings=get_settings())
    app.state.bootstrap = bootstrap
    logger.info("Bootstrap initialized and set in app state")

    # Ceder el control a FastAPI
    yield


def create_application() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.

    Returns:
        Instancia configurada de FastAPI
    """
    logger.info("Creating FastAPI application")
    app = FastAPI(
        title="Customer Support Agente",
        description="API para un agente de soporte al cliente que utiliza LLMs y LangChain.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configurar middlewares
    logger.info("Setting up middlewares")
    setup_middlewares(app=app)

    logger.info("Setting up routers")
    setup_routers(app=app)

    logger.info("Setting up static files")
    setup_static(app=app)

    logger.info("FastAPI application created successfully")
    return app


try:
    # Crear la instancia de la aplicación
    app = create_application()
except Exception as err:
    logger.error(f"Error creating FastAPI application: {err}")
    raise err
