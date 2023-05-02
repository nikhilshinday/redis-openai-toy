import aioredis
import openai
from typer import Typer

from utils import run_until_complete


app = Typer()


class RedisStreamEnqueuer:
    def __init__(self, stream: str):
        self.stream = stream
        self.redis = None

    async def __aenter__(self):
        self.redis = await aioredis.Redis()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.redis.xadd(self.stream, {"token": ""})
        await self.redis.expire(self.stream, 60)
        await self.redis.close()

    async def enqueue(self, token: str):
        await self.redis.xadd(self.stream, {"token": token})


@app.command()
@run_until_complete
async def prompt(prompt: str, stream: str):
    async with RedisStreamEnqueuer(stream) as enqueuer:
        async for chunk in await openai.ChatCompletion.acreate(
            messages=[{"role": "user", "content": prompt}], model="gpt-4", stream=True
        ):
            delta = chunk.choices[0].delta
            if "content" in delta:
                await enqueuer.enqueue(delta.content)


if __name__ == "__main__":
    app()
