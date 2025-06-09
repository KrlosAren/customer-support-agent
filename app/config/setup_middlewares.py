from fastapi import FastAPI

def setup_middlewares(app: FastAPI) -> FastAPI:
    """
    Setup middleware for the FastAPI application.
    This function is called to configure middleware components.
    """
    # Example: Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust as needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

