import asyncio
import random
import time

from fxpkg.util.async_executor import AsyncExecutor

async def assignment(i, t):
    print(f'id: {i}, time: {t}, begin')
    await asyncio.sleep(t)
    print(f'id: {i}, time: {t}, end')
    return i, t


async def main():
    executor = AsyncExecutor()
    ts = [random.random()*3 for i in range(20)]
    time_start = time.time()
    futures = [await executor.submit(assignment(i, ts[i])) for i in range(20)]
    results = [await future for future in futures]
    time_end = time.time()
    print(results)
    print(f'time: {time_end-time_start}')
    # await executor.wait_done()


def test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())