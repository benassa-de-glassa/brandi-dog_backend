import logging

import socketio

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*')    # logger=False)


@sio.event
async def connect(sid, environ):
    print('connect', sid)


@sio.event
async def disconnect(sid):
    print('disconnect', sid)
