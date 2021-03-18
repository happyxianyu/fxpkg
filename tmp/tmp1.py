import asyncio
from collections import deque
import time

class AsyncPipeline:
    class RunningData:
        def __init__(self, res_q, result_lock, uncomplete_num, res_callback):
            self.uncomplete_num = uncomplete_num
            if res_callback == None:
                self.res_q = res_q
                self.result_lock = result_lock
            else:
                self.res_callback = res_callback

    def __init__(self, tasks = None, workers_num = 3, share_result = None, res_callback = None):
        '''
        tasks为要执行的任务
        workers_num为最大并行执行任务
        share_result为另一个AsyncPipeline对象，表示和其共用一个结果队列
        res_callback处理结果的函数，参数为(result, exception)

        如果设置了res_callback，则结果队列和结果锁将被忽略，该参数和share_result的对象共享
        '''
        assert(workers_num > 0)

        self.loop = asyncio.get_event_loop()

        self.running_event = asyncio.Event()  
        if tasks!= None and len(tasks):
            self.running_event.set()
            self.wait_q = deque(tasks)
        else:
            self.wait_q = deque()

        if share_result:
            self.running_data = share_result.running_data
            self.running_data.uncomplete_num+=len(self.wait_q)
        else:
            if res_callback == None:
                self.running_data = self.RunningData(deque(), asyncio.Lock(), len(self.wait_q), res_callback)
            else:
                self.running_data = self.RunningData(None, None, len(self.wait_q), res_callback)

        self.terminate_flag = False
        self.workers = [self.loop.create_task(self.worker()) for _ in range(workers_num)]

    async def worker(self):
        while True:
            await self.running_event.wait()
            if self.terminate_flag:
                return
            
            if len(self.wait_q):         
                task = self.wait_q.popleft()

                res, e = None, None
                try:
                    res = await task
                except BaseException as e1:
                    e = e1

                running_data = self.running_data
                
                if running_data.res_callback == None:
                    result_lock = running_data.result_lock
                    res_q = running_data.res_q
                    res_q.append((res, e))

                running_data.uncomplete_num-=1

                if result_lock.locked():
                    result_lock.release()    
            else:
                self.running_event.clear()

    def put_task(self, task):
        self.wait_q.append(task)
        self.running_data.uncomplete_num += 1
        self.running_event.set()

    def run(self):
        '''
        每次生成(res, exception)
        若没有exception则exception为None
        '''
        while self.wait():
            res_q = self.running_data.res_q
            while len(res_q):
                yield res_q.popleft()
    
    async def run_async(self):
        while await self.wait_async():
            res_q = self.running_data.res_q
            while len(res_q):
                yield res_q.popleft()

    def get_result_queue(self):
        return self.running_data.res_q

    def finished(self):
        '''
        检测所有任务是否都已完成
        '''
        return self.running_data.uncomplete_num <= 0

    async def wait_async(self):
        if not self.finished():
            await self.running_data.result_lock.acquire()
            return True
        return False
            
    def wait(self):
        '''
        等待下一个结果运行完成
        如果还有任务未完成并成功运行返回True，否则返回False
        '''
        if not self.finished():
            self.loop.run_until_complete(self.wait_async())
            return True
        return False

    def pop_result(self):
        '''
        使用前应当检测has_result，若无结果抛出异常
        '''
        return self.running_data.res_q.popleft()
    
    def has_result(self):
        '''
        若结果队列中有结果则返回True，否则返回False
        '''
        return len(self.running_data.res_q) > 0

    async def clear_workers(self):
        workers = self.workers
        self.terminate_flag = True
        self.running_event.set()
        for worker in workers:
            await worker
        self.workers = []

    async def aclose(self):
        await self.clear_workers()

    def close(self):   
        future = self.loop.create_task(self.aclose())
        if not self.loop.is_running():
            self.loop.run_until_complete(self.aclose())
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *execinfo):
        await self.clear_workers()

    def __enter__(self):
        return self
    
    def __exit__(self, *execinfo):
        self.close() 
        





async def foo (n):
    print('Waiting: ', n)
    await asyncio.sleep(n)
    print('Completing: ', n)
    return n

async def run_cmd(cmd, cwd = None):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd = cwd
        )

    stdout, stderr = await proc.communicate()
    return stdout, stderr

async def git_proc(url):
    import os
    dst = r'D:\tmp\tmp'
    os.chdir(dst)

    cmd = f'git clone --depth=1 {url}'
    await run_cmd(cmd, dst)
    return url


e = AsyncPipeline(workers_num=2)


urls = [
    'https://github.com/CharlesPikachu/Tools.git',
    'https://github.com/offu/WeRoBot.git',
    'https://github.com/pandas-profiling/pandas-profiling.git',
    'https://github.com/encode/httpx.git'
]

for url in urls:
    e.put_task(git_proc(url))

for res in e.run():
    print(f'result: {res}')

e.close()