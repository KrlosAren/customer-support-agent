from langchain_core.runnables import Runnable, RunnableConfig


from app.agents.supervisor.state import TraveleAgentState

from app.utils.logger import get_logger

logger = get_logger(name=__name__)


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: TraveleAgentState, config: RunnableConfig):
        while True:
            logger.info("Assistant is running")
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            if not passenger_id:
                raise ValueError("Passenger ID is required")
            logger.info(f"Using passenger ID: {passenger_id}")

            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
