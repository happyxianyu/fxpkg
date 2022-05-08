import asyncio
import atexit
import weakref

from .coro_queue import CoroDeque

__all__ = ['CoroExecutor']

_workers_ref = set()


@atexit.register
def _cleanup():
    for ref in list(_workers_ref):  # 避免changed size
        worker = ref()
        if worker is not None:
            worker.stop_b()

class CoroExecutor:
    """
    A coroutine executor

    suffix meaning:
    a: async version
    b: block version
    nw: no wait
    """
    def __init__(self, workers_num=3):
        self._q = CoroDeque()
        self.workers = [self.Worker(self._q) for _ in range(workers_num)]

    class Worker:
        def __init__(self, q):
            self.stop_flag = False
            self.stop_event = asyncio.Event()
            self.waiting_flag = False
            self.running_flag = False
            self.q: CoroDeque = q
            self._in = []

            loop = asyncio.get_event_loop()
            self.task: asyncio.Task = loop.create_task(self.work())
            ref = weakref.ref(self)
            self._ref = ref
            _workers_ref.add(ref)

        async def work(self):
            q = self.q
            while not self.stop_flag:
                stop_event = self.stop_event

                # 等待 stop event 或 任务队列，如果 stop event 返回则直接终止该程序
                self.waiting_flag = True
                event = asyncio.Event()

                stop_future = asyncio.ensure_future(stop_event.wait())
                pop_future = asyncio.ensure_future(q.popout())
                stop_future.add_done_callback(lambda _:event.set())
                pop_future.add_done_callback(lambda _:event.set())

                await event.wait()
                if stop_future.done():
                    pop_future.cancel()
                    self.waiting_flag = False
                    return

                term = pop_future.result()
                #
                # for coro in asyncio.as_completed([stop_event.wait(), q.popout()]):
                #     term = await coro
                #     self.waiting_flag = False
                #     if stop_event.is_set():
                #         return
                #     break

                if term is CoroDeque.NoWait:
                    return
                task, future = term

                try:
                    self.running_flag = True
                    result = await task
                except Exception as e:
                    future.set_exception(e)
                else:
                    future.set_result(result)
                finally:
                    self.running_flag = False
                    await asyncio.sleep(0)  # 转移控

        async def stop(self):
            if self.stopped():
                return

            self.stop_flag = True
            self.stop_event.set()
            await self.task
            self.task = None

        def stop_b(self):
            loop = asyncio.get_event_loop()

            if loop.is_running():
                loop.create_task(self.stop())
            else:
                loop.run_until_complete(self.stop())
            self.task = None

        def terminate(self):
            if self.stopped():
                return
            if self.waiting_flag is True:
                self.stop_b()
                return
            self.task.cancel()
            self.stop_b()
            self.task = None

        def stopped(self):
            return self.task is None

        def __del__(self):
            self.stop_b()
            _workers_ref.remove(self._ref)

    async def submit(self, task, front = False) -> asyncio.Future:
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        term = task, future
        if front:
            await self._q.appendleft(term)
        else:
            await self._q.put(term)
        return future

    def submit_nw(self, task, front = False):
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        term = task, future
        if front:
            self._q.appendleft_nw(term)
        else:
            self._q.put_nw(term)
        return future

    async def run(self):
        while True:
            await self._q.wait_pop()

    async def wait_done(self):
        await self._q.wait_done()

    @property
    def wokers_num(self):
        return len(self.workers)

    def shutdown(self):
        for worker in self.workers:
            worker.terminate()
        self.workers.clear()

    async def close(self):
        workers = self.workers
        for worker in self.workers:
            await worker.stop()
        self.workers.clear()

    def close_b(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.close())
        else:
            loop.run_until_complete(self.close())
        self.workers.clear()

    def closed(self):
        return len(self.workers) == 0
