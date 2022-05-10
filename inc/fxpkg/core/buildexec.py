import asyncio

from cbutil import CoroExecutor

class BuildExecutor:
    def __init__(self):
        self.donwload_executor = CoroExecutor()
        self.heavy_proc_executor = CoroExecutor(1)
        self.light_proc_executor = CoroExecutor(10)


    def run_download(self, coro) -> asyncio.Future:
        return self.donwload_executor.submit_nw(coro)

    def run_light_proc(self, coro) -> asyncio.Future:
        return self.light_proc_executor.submit_nw(coro)

    def run_heavy_proc(self, coro) -> asyncio.Future:
        return self.heavy_proc_executor.submit_nw(coro)


        