from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/home")
async def home(request: Request) -> HTMLResponse:
    """
    Renderiza la página de inicio del chat.

    Args:
        request: Request object from FastAPI
    """
    return request.app.state.bootstrap.components.templates.TemplateResponse(
        request=request, name="index.html"
    )
