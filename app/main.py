import datetime
import logging

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

import uvicorn
import socketio
from app.api import games, chats, users

origins = [
    "*",
]

app = FastAPI(
    # title=config.PROJECT_NAME,
    # description=config.PROJECT_NAME,
    # version=config.PROJECT_VERSION,
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.on_event('startup')
async def startup_event():
    # db_connection = r.connect('localhost', 28015).repl()
    pass

app.include_router(
    games.router,
    prefix='/v1'
    )

app.include_router(
    chats.router,
    prefix='/v1'
    )

app.include_router(
    users.router,
    prefix='/v1'
    )
# mount the socket coming from the routers/game.py file
# sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)

# app.add_route("/socket.io/", route=sio_asgi_app)
# app.add_websocket_route("/socket.io/", sio_asgi_app)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000 , debug=True)