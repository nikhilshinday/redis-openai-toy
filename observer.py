import os
from typer import Typer

import websockets

from utils import run_until_complete


app = Typer()


@app.command()
@run_until_complete
async def consume_websocket(stream: str):
    chunks = []
    async with websockets.connect(
        f"ws://localhost:8000/listen", extra_headers=[("Authorization", stream)]
    ) as websocket:
        try:
            while True:
                chunk = await websocket.recv()
                chunks.append(chunk)
                os.system("clear")
                print("".join(chunks))
        except KeyboardInterrupt:
            await websocket.close()
            return
        except websockets.ConnectionClosed:
            return


if __name__ == "__main__":
    app()
