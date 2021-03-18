import asyncio
from collections import deque

class AsyncDeque:
    def __init__(self, iterable = None, maxlen = None):
        kwargs = {}
        if iterable != None:
            kwargs['iterable'] = iterable
        if maxlen != None:
            kwargs['maxlen'] = maxlen
        self._q = deque(**kwargs)
        self.loop = asyncio.get_event_loop()
        self._not_full_event = asyncio.Event()  # set when not full
        self._not_empty_event = asyncio.Event() # set when not empty
        if len(self):
            self._when_not_empty()
            if len(self) >= maxlen:
                self._when_full()
            else:
                self._when_not_full()
        else:
            self._when_empty()
            self._when_not_full()

    @property
    def maxlen(self):
        return self._q.maxlen

    def __len__(self):
        return len(self._q)

    def append_nw(self, item):
        self._q.append(item)
        self._when_not_empty()

    async def append(self, item):
        if self.is_full():
            self._when_full()
            await self._not_full_event.wait()
        self._q.append(item)
        self._when_not_empty()

    def appendleft_nw(self, item):
        self._q.appendleft(item)
        self._when_not_empty()

    async def appendleft(self, item):
        if self.is_full():
            self._when_full()
            await self._not_full_event.wait()
        self._q.appendleft(item)
        self._when_not_empty()

    def pop_nw(self):
        res = self._q.pop()
        self._when_not_full()
        return res

    async def pop(self):
        if not len(self):
            self._when_empty()
            await self._not_empty_event.wait()
        self._when_not_full()
        return self._q.pop()
        
    def popleft_nw(self):
        res = self._q.popleft()
        self._when_not_full()
        return res

    async def popleft(self):
        if not len(self):
            self._when_empty()
            await self._not_empty_event.wait()
        self._when_not_full()
        return self._q.popleft()

    def put_nw(self, item):
        self.append_nw(item)

    async def put(self, item):
        await self.append(item)

    def popout_nw(self):
        return self.popleft_nw()

    async def popout(self):
        return await self.popleft()

    async def wait(self):
        '''
        等待不为空
        '''
        if len(self) == 0:
            await self._not_empty_event.wait()
    
    def wait_b(self):
        if len(self) == 0:
            self.loop.run_until_complete(
                self._not_empty_event.wait())

    async def wait_not_full(self):
        if self.is_full():
            await self._not_full_event.wait()

    def wait_not_full_b(self):
        if self.is_full():
            self.loop.run_until_complete(
                self._not_full_event.wait())
        
    def is_full(self):
        maxlen = self.maxlen
        return self.maxlen!= None and len(self) >= maxlen
    
    def __str__(self):
        return self.to_str(str)

    def __repr__(self):
        return self.to_str(repr)

    def to_str(self, f = str):
        return f'AsyncDeque{f(self._q)[5:]}'    

    def __iter__(self):
        return iter(self._q) 
    
    def _when_empty(self):
        event = self._not_empty_event
        if event.is_set():
            event.clear()
    
    def _when_not_empty(self):
        event = self._not_empty_event
        if not event.is_set():
            event.set()

    def _when_full(self):
        event = self._not_full_event
        if event.is_set():
            event.clear()
    
    def _when_not_full(self):
        event = self._not_full_event
        if not event.is_set():
            event.set()
