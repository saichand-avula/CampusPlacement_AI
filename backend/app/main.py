from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.upload import router as upload_router
from store_connection import init_store, close_store
from sqllite_connection import init_database, close_database
from checkpoint_connection import init_checkpointer, close_checkpointer
from graphs.graph import init_graph
from assistant.assistant_graph import init_graph as init_assistant_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    store = await init_store()
    checkpointer = await init_checkpointer()

    init_database()

    init_graph(store, checkpointer=None)              # workflow graph — NO checkpointer (avoids SQLite lock deadlock)
    init_assistant_graph(store, checkpointer)          # assistant graph — uses checkpointer for persistence

    yield

    close_database()
    await close_store()
    await close_checkpointer()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(upload_router)