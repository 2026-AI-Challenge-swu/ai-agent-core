from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import os
from dotenv import load_dotenv

from src.ai_agent_core.api.router import api_router
from src.ai_agent_core.config.config import load_config
from src.ai_agent_core.core.middleware import RequestLogMiddleware

from ai_common.llm.gpt import GPT
from ai_common.logging.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("starting...")
    load_dotenv()
    app.state.config = load_config()
    app.state.config.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    app.state.logger = setup_logger()
    app.state.llm = GPT(app.state)
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

app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        # "main:app",
        "src.ai_agent_core.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True, # 개발용
        # workers=3
    )
