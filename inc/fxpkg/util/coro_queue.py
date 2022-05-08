import asyncio
import logging
from collections import deque
from contextlib import contextmanager, asynccontextmanager

__all__ = ['CoroDeque', 'CoroEvent']

class CoroEvent(asyncio.Event):
    def __init__(self):
        self.wait_num = 0
        super().__init__()

    async def wait(self):
        self.wait_num += 1
        await super().wait()
        self.wait_num -= 1


class CoroDeque:
    class NoWait:
        pass

    def __init__(self, iterable=None, maxlen=None):
        kwargs = {}
        if iterable != None:
            kwargs['iterable'] = iterable
        if maxlen != None:
            kwargs['maxlen'] = maxlen
        self._q = deque(**kwargs)
        self.loop = asyncio.get_event_loop()

        self._pop_event = asyncio.Event()
        self._put_event = asyncio.Event()
        self._pop_lock = asyncio.Lock()
        self._put_lock = asyncio.Lock()
        self.pop_wait_num = 0
        self.put_wait_num = 0

        if self.is_full():
            self._put_lock.acquire()
        if len(self) == 0:
            self._pop_lock.acquire()

    @property
    def maxlen(self):
        return self._q.maxlen

    def __len__(self):
        return len(self._q)

    def append_nw(self, item):
        self._q.append(item)
        self._after_put()

    async def append(self, item):
        async with self._when_put():
            self._q.append(item)

    def appendleft_nw(self, item):
        self._q.appendleft(item)
        self._after_put()

    async def appendleft(self, item):
        async with self._when_put():
            self._q.appendleft(item)

    def pop_nw(self):
        res = self._q.pop()
        self._after_pop()
        return res

    async def pop(self):
        async with self._when_pop():
            res = self._q.pop()
        return res

    def popleft_nw(self):
        res = self._q.popleft()
        self._after_pop()
        return res

    async def popleft(self):
        async with self._when_pop():
            res = self._q.popleft()
        return res

    def put_nw(self, item):
        self.append_nw(item)

    async def put(self, item):
        await self.append(item)

    def popout_nw(self):
        return self.popleft_nw()

    async def popout(self):
        return await self.popleft()

    async def wait(self):
        """
        等待不为空
        """
        while len(self) == 0:
            async with self._acquire_pop_lock():  # 获取并释放
                pass

    async def wait_pop(self):
        await self._pop_event.wait()

    async def wait_done(self):
        while len(self) != 0:
            await self._pop_event.wait()

    def wait_b(self):
        if len(self) == 0:
            self.loop.run_until_complete(
                self.wait())

    async def wait_not_full(self):
        while self.is_full():
            async with self._acquire_put_lock():  # 获取并释放
                pass

    def wait_not_full_b(self):
        if self.is_full():
            self.loop.run_until_complete(
                self.wait_not_full())

    async def push_no_waits(self):
        '''
        放入停止等待信息，直到当前所有等待取出数据的对象不再等待
        '''
        NoWait = self.NoWait
        wait_num = self.pop_wait_num
        put_num = wait_num - len(self)
        if put_num > 0:
            for _ in range(put_num):
                await self.put(NoWait)

    def is_full(self):
        maxlen = self.maxlen
        return self.maxlen is not None and len(self) >= maxlen

    def clear(self):
        self._q.clear()
        self._after_pop()

    def __str__(self):
        return self.to_str(str)

    def __repr__(self):
        return self.to_str(repr)

    def to_str(self, f=str):
        return f'AsyncDeque{f(self._q)[5:]}'

    def __iter__(self):
        return iter(self._q)

    def _after_pop(self):
        self._set_event(self._pop_event)
        self._pop_event = asyncio.Event()
        self._release_lock(self._put_lock)

    @asynccontextmanager
    async def _acquire_pop_lock(self):
        try:
            while len(self) == 0:
                self.pop_wait_num += 1
                await self._pop_lock.acquire()
                self.pop_wait_num -= 1
            yield
        finally:
            if len(self) > 0:  # not empty
                self._release_lock(self._pop_lock)

    @asynccontextmanager
    async def _when_pop(self):
        # before pop
        try:
            if len(self) == 0:
                async with self._acquire_pop_lock():
                    yield  # pop
            else:
                yield  # pop
        # after pop
        finally:
            self._after_pop()

    def _after_put(self):
        self._set_event(self._put_event)
        self._put_event = asyncio.Event()
        self._release_lock(self._pop_lock)

    @asynccontextmanager
    async def _acquire_put_lock(self):
        try:
            while self.is_full():
                self.put_wait_num += 1
                await self._put_lock.acquire()
                self.put_wait_num -= 1
            yield  # put
        finally:
            if not self.is_full():
                self._release_lock(self._put_lock)

    @asynccontextmanager
    async def _when_put(self):
        try:
            # before put
            if self.is_full():
                async with self._acquire_put_lock():
                    yield  # put
            else:
                yield  # put
        finally:
            # after put
            self._after_put()

    @staticmethod
    def _set_event(*events):
        for event in events:
            if not event.is_set():
                event.set()

    @staticmethod
    def _clear_event(*events):
        for event in events:
            if event.is_set():
                event.clear()

    @staticmethod
    def _release_lock(*locks):
        for lock in locks:
            if lock.locked():
                lock.release()
