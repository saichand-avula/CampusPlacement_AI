from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.newchat import router as newchat_router
from graphs.sqlliteconnection import init_store, close_store
from graphs.graph import init_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = await init_store()
    init_graph(store)
    yield
    await close_store()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(newchat_router)