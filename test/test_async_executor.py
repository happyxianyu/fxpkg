import asyncio
import random


from fxpkg.util.async_executor import AsyncExecutor

async def assignment(i, t):
    print(f'id:{i}, time:{t}, begin')
    await asyncio.sleep(t)
    print(f'id:{i}, time:{t}, end')


async def main():
    executor = AsyncExecutor()
    for i in range(20):
        t = random.random()
        await executor.submit(assignment(i, t))


def test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())