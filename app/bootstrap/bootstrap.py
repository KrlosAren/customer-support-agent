from typing import Optional

from app.config.settings import Settings
from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(name=__name__)


class AppComponents:
    """Contenedor para componentes de la aplicación."""

    def __init__(self, retriever):
        """
        Inicializa los componentes con las dependencias inyectadas.
        """
        self.retriever = retriever


class Bootstrap:
    """
    Responsable de inicializar y proporcionar los componentes de la aplicación.
    Implementa un patrón Singleton.
    """

    logger.info("Initializing Bootstrap")
    _instance: Optional["Bootstrap"] = None
    _components: Optional[AppComponents] = None

    def __new__(cls, settings: Settings = None):
        if cls._instance is None:
            cls._instance = super(Bootstrap, cls).__new__(cls)
            # Inicializar componentes si no existen
            if cls._components is None:
                if settings is None:
                    settings = get_settings()
                cls._initialize_components(settings=settings)
        return cls._instance

    @classmethod
    def _initialize_components(cls, settings: Settings):
        """
        Inicializa los componentes de la aplicación.

        Args:
            settings: Configuración de la aplicación
        """
        from app.services.vectorstore.vector_store import VectorStoreRetriever
        import requests
        import openai
        import re

        logger.info("Initializing components")

        response = requests.get(
            url=settings.faq_url,
            timeout=10,
        )
        response.raise_for_status()
        faq_text = response.text

        docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]

        ## open ai
        oai_client = openai.OpenAI()

        retriever = VectorStoreRetriever.from_docs(docs=docs, oai_client=oai_client)

        components = AppComponents(retriever=retriever)

        cls._components = components
        logger.info("Components initialized successfully")

    @property
    def components(self) -> AppComponents:
        """
        Proporciona acceso a los componentes de la aplicación.

        Returns:
            Contenedor de componentes

        Raises:
            RuntimeError: Si los componentes no han sido inicializados.
        """
        if self._components is None:
            raise RuntimeError("AppComponents have not been initialized.")
        return self._components

    @classmethod
    def reset(cls):
        """Reinicia el singleton (útil para pruebas)."""
        cls._instance = None
        cls._components = None


def get_bootstrap(settings: Settings = None) -> Bootstrap:
    """
    Función global para acceder a Bootstrap.

    Args:
        settings: Configuración opcional (si no se proporciona, se usa la global)

    Returns:
        Instancia de Bootstrap
    """
    return Bootstrap(settings=settings)
