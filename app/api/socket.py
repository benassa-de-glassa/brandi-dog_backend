import logging

import socketio

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*')    # logger=False)


@sio.event
async def connect(sid, environ):
    logging.info(f'SIO connection: {sid}')


@sio.event
async def disconnect(sid):
    logging.info(f'SIO disconnected: {sid}')
