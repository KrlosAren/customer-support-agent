from fastapi import APIRouter, HTTPException, Request

from app.utils.logger import get_logger

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

logger = get_logger(name=__name__)


@router.post("/")
async def chat(request: Request, message: str):
    try:
        thread_id = "hola"
        config = {
            "configurable": {
                "passenger_id": "3442 587242",
                "thread_id": thread_id,
            }
        }

        agent = request.app.state.bootstrap.components.agent
        if not agent:
            logger.error("Agent not initialized")
            raise HTTPException(status_code=500, detail="Agent not initialized")

        result = await agent.ainvoke(
            {"input": message},
            config=config,
        )

        if not result:
            logger.error("No response from agent")
            raise HTTPException(status_code=404, detail="No response from agent")

        logger.info(f"Agent response: {result}")
        if not result.get("messages"):
            logger.warning("No messages found in the result")
            raise HTTPException(status_code=404, detail="No messages found")

        return {
            "response": (
                result.get("messages")[-1].content
                if result.get("messages")
                else "No messages found"
            )
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
