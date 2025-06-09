from fastapi import APIRouter, WebSocket
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

logger = get_logger(name=__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    thread_id = "hola"
    config = {
        "configurable": {
            "passenger_id": "3442 587242",
            "thread_id": thread_id,
        }
    }
    agent = websocket.app.state.bootstrap.components.agent
    if not agent:
        logger.error("Agent not initialized")
        await websocket.close(code=1011, reason="Agent not initialized")
        return

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")

            result = await agent.ainvoke(
                {"input": data},
                config=config,
            )

            if not result:
                logger.error("No response from agent")
                await websocket.send_text("No response from agent")
                continue

            messages = result.get("messages")
            if not messages:
                logger.warning("No messages found in the result")
                await websocket.send_text("No messages found")
                continue

            response_text = (
                messages[-1].content
                if hasattr(messages[-1], "content")
                else messages[-1].get("content", "")
            )
            logger.info(f"Agent response: {response_text}")

            await websocket.send_text(response_text)

    except Exception as e:
        logger.exception("Unexpected error in WebSocket")
        await websocket.close(code=1011, reason=str(e))
