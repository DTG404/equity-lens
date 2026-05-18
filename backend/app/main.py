from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.db import close_db, init_db
from app.core.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()
    await close_db()


app = FastAPI(title='Equity Lens API', lifespan=lifespan)
app.include_router(router, prefix='/api')
