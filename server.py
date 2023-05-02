import aioredis
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/listen")
async def listen(websocket: WebSocket):
    stream = websocket.headers["Authorization"]
    await websocket.accept()
    redis = await aioredis.Redis()
    previous_id = "0-0"
    while True:
        messages = await redis.xread({stream: previous_id}, block=60)
        if messages:
            for new_id, data in messages[0][1]:
                previous_id = new_id
                chunk = data[b"token"].decode("utf-8")
                if chunk == "":
                    await websocket.close()
                    break
                await websocket.send_text(chunk)
