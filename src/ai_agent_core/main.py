from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from src.ai_agent_core.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("starting...")
    # app.state.model = load_model()
    # app.state.db = await connect_db()

    yield

    # Shutdown
    print("shutting down...")
    # await app.state.db.close()


app = FastAPI(
    title="ai-agent-core",
    version="1.0.0",
    lifespan=lifespan,
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True, # 개발용
        # workers=3
    )
