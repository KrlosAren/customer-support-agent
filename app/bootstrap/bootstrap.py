from typing import Optional

from app.agents.base.agent import Assistant
from app.agents.flights.tools import create_flight_booking_tools
from app.agents.hotels.tools import create_hotel_booking_tools
from app.agents.cars.tools import create_cars_booking_tools
from app.agents.base.tools import create_lookup_policy_tool
from app.agents.activities.tools import create_activities_tools
from app.agents.supervisor.graph import supervisor_graph
from app.agents.supervisor.state import TravelerAgentState
from app.config.settings import Settings
from app.config.settings import get_settings
from app.services.vectorstore.vector_store import VectorStoreRetriever
from app.utils.logger import get_logger

from langgraph.graph import StateGraph

from app.agents.base.prompts import primary_assistant_prompt
from langchain_openai.chat_models import ChatOpenAI

from langchain_core.runnables import RunnableSerializable

from fastapi.templating import Jinja2Templates


logger = get_logger(name=__name__)


class AppComponents:
    """Contenedor para componentes de la aplicación."""

    def __init__(
        self,
        retriever: VectorStoreRetriever,
        agent: RunnableSerializable,
        templates: Jinja2Templates,
    ):
        """
        Inicializa los componentes con las dependencias inyectadas.
        """
        self.retriever = retriever
        self.agent = agent
        self.templates = templates


class Bootstrap:
    """
    Responsable de inicializar y proporcionar los componentes de la aplicación.
    Implementa un patrón Singleton.
    """

    logger.info("Initializing Bootstrap")
    _instance: Optional["Bootstrap"] = None
    _components: Optional[AppComponents] = None

    def __new__(cls, settings: Settings = None) -> "Bootstrap":
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

        oai_client = openai.OpenAI()

        retriever = VectorStoreRetriever.from_docs(docs=docs, oai_client=oai_client)

        llm = ChatOpenAI(model=settings.llm_model)
        logger.info(f"Initialized LLM: {settings.llm_model}")

        tools = []
        policies_tools = create_lookup_policy_tool(retriever=retriever)
        flight_tools = create_flight_booking_tools(db_path=settings.db_path)
        hotel_tools = create_hotel_booking_tools(db_path=settings.db_path)
        car_tools = create_cars_booking_tools(db_path=settings.db_path)
        activities_tools = create_activities_tools(db_path=settings.db_path)

        tools += (
            policies_tools + flight_tools + hotel_tools + car_tools + activities_tools
        )
        logger.info(f"Initialized {len(tools)} tools")

        runnable_with_tools = primary_assistant_prompt | llm.bind_tools(tools=tools)
        logger.info("Initialized runnable with tools")

        builder = StateGraph(TravelerAgentState)
        agent = supervisor_graph(
            builder=builder,
            tools=tools,
            assistant=Assistant(runnable=runnable_with_tools),
        )

        templates = Jinja2Templates(directory="app/templates")

        components = AppComponents(
            retriever=retriever, agent=agent, templates=templates
        )

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
