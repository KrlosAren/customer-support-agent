from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.bootstrap.bootstrap import get_bootstrap
from app.config.settings import get_settings

from app.utils.logging import get_logger

logger = get_logger(name=__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app."""

    bootstrap = get_bootstrap(settings=get_settings())
    app.state.bootstrap = bootstrap

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
    # setup_middlewares(app)

    # Crear función para la dependencia de la base de datos

    # Importar y configurar routers
    # from app.router.router import setup_routers

    # setup_routers(app)

    logger.info("FastAPI application created successfully")
    return app


# Crear la instancia de la aplicación
app = create_application()
