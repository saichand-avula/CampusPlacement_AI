from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.newchat import router as newchat_router
from store_connection import init_store, close_store
from sqllite_connection import init_database,close_database
from graphs.graph import init_graph
from assistant.assistant_graph import init_graph as init_assistant_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    store = await init_store()

    init_database()

    init_graph(store)          # workflow graph
    init_assistant_graph(store) # assistant graph

    yield

    close_database()
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