import asyncio
from collections import deque
from fxpkg.util import Path


class AsyncPipelineStage:
    class RunningData:
        def __init__(self, out_q, step_event, uncomplete_num, output_callback):
            self.uncomplete_num = uncomplete_num
            self.complete_num = 0
            self.out_q = out_q
            self.step_event = step_event
            self.output_callback = output_callback 

    def __init__(self, tasks = None, workers_num = 3, share_output = None, output_callback = None):
        '''
        tasks为要执行的任务
        workers_num为最大并行执行任务
        share_output为另一个AsyncPipelineStage对象，表示和其共用一个结果队列
        output_callback处理结果的函数，参数为(output, exception)

        如果设置了output_callback，则结果队列将被忽略，该参数和share_output的对象共享
        '''
        assert(workers_num > 0)

        self.loop = asyncio.get_event_loop()

        self.running_event = asyncio.Event()  
        self.done_event = asyncio.Event()

        if tasks!= None and len(tasks):
            self.running_event.set()
            self.in_q = deque(tasks)
        else:
            self.done_event.set()
            self.in_q = deque()

        if share_output:
            self.running_data = share_output.running_data
            self.running_data.uncomplete_num+=len(self.in_q)
        else:
            self.running_data = self.RunningData(deque(), asyncio.Event(), len(self.in_q), output_callback)

        self.running_num = 0
        self.terminate_flag = False
        self.workers = [self.loop.create_task(self.worker()) for _ in range(workers_num)]


    async def worker(self):
        while True:
            await self.running_event.wait()
            self.running_num+=1

            if self.terminate_flag:
                return
            
            if len(self.in_q):         
                task = self.in_q.popleft()

                res, e = None, None
                try:
                    res = await task
                except BaseException as e1:
                    e = e1

                running_data = self.running_data
                output_callback = running_data.output_callback

                if output_callback == None:
                    out_q = running_data.out_q
                    out_q.append((res, e))
                else:
                    output_callback(res,e)

                step_event = running_data.step_event
                if not step_event.is_set():
                    step_event.set()

                running_data.uncomplete_num-=1
                running_data.complete_num+=1
            else:
                self.running_num-=1
                self.running_event.clear()
                self.done_event.set()

    def put_task(self, task):
        self.in_q.append(task)
        self.running_data.uncomplete_num += 1
        if not self.done_event.is_set():
            self.done_event.clear()
        if not self.running_event.is_set():
            self.running_event.set()


    def set_output_callback(self, callback):
        self.running_data.output_callback = callback

    def set_prestage_callback(self, callback):
        '''
        callback是接收来自前stage输出的协程，设置后只在AsyncPipeline中有效
        callback的参数为(res, exception)
        '''
        self.prestage_callback = callback


    def run(self):
        '''
        每次生成(res, exception)
        若没有exception则exception为None
        '''
        while self.wait():
            out_q = self.running_data.out_q
            while len(out_q):
                yield out_q.popleft()
    
    async def run_async(self):
        while await self.wait_async():
            out_q = self.running_data.out_q
            while len(out_q):
                yield out_q.popleft()

    def get_output_queue(self):
        return self.running_data.out_q

    def get_done_num(self):
        return self.running_data.complete_num

    def done(self):
        '''
        检测所有任务是否都已完成
        '''
        return self.running_data.uncomplete_num <= 0

    async def wait_async(self):
        if not self.done():
            step_event = self.running_data.step_event
            if step_event.is_set():
                step_event.clear()
            await step_event.wait()
            return True
        return False

    async def wait_done_aysnc(self):
        if not self.done():
            await self.done_event.wait()
    
            
    def wait(self):
        '''
        等待下一个结果运行完成
        如果还有任务未完成并成功运行返回True，否则返回False
        '''
        if not self.done():
            self.loop.run_until_complete(self.wait_async())
            return True
        return False

    def wait_done(self):
        if not self.done():
            self.loop.run_until_complete(self.wait_done_aysnc())

    def pop_output(self):
        '''
        使用前应当检测has_output，若无结果抛出异常
        '''
        return self.running_data.out_q.popleft()
    
    def has_output(self):
        '''
        若结果队列中有结果则返回True，否则返回False
        '''
        return len(self.running_data.out_q) > 0

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
        task = self.loop.create_task(self.aclose())
        if not self.loop.is_running():
            self.loop.run_until_complete(task)
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *execinfo):
        await self.aclose()

    def __enter__(self):
        return self
    
    def __exit__(self, *execinfo):
        self.close() 
        





class AsyncPipeline:
    '''
    除了显式说明，否则要求全部加入的stage必须设置了prestage_callback
    '''
    def __init__(self, stages = None):
        if stages == None:
            stages = []
        self.stages = []
        self.total_task_num = 0

    def put_task(self, task):
        self.total_task_num+=1
        stage = self.stages[0]
        stage.put_task(task)

    def done(self):
        last_stage = self.stages[-1]
        return last_stage.get_done_num() >= self.total_task_num

    async def wait_async(self):
        last_stage = self.stages[-1]
        if not self.done():
            step_event = last_stage.running_data.step_event
            if step_event.is_set():
                step_event.clear()
            await step_event.wait()
            return True
        return False

    def wait(self):
        last_stage = self.stages[-1]
        if not self.done():
            last_stage.loop.run_until_complete(self.wait_async())
            return True
        return False


    async def run_async(self):
        last_stage = self.stages[-1]
        while await self.wait_async():
            out_q = last_stage.running_data.out_q
            while len(out_q):
                yield out_q.popleft()

    def run(self):
        '''
        每次生成(res, exception)
        若没有exception则exception为None
        '''
        last_stage = self.stages[-1]
        while self.wait():
            out_q = last_stage.running_data.out_q
            while len(out_q):
                yield out_q.popleft()

        
    def _make_output_callback(self, next_stage):
        def output_callback(res, e):
            next_stage.put_task(
                next_stage.prestage_callback(res, e))

        return output_callback

    def _set_output_callback(self, i):
        stages = self.stages
        stages[i].set_output_callback(
            self._make_output_callback(stages[i+1]))

    def set_stages(self, stages):
        for i in range(len(stages)- 1):
            self._set_output_callback(i)
        self.stages = stages

    def set_first_stage(self, stage=None):
        '''
        若stage为None，则创建一个默认stage
        '''
        if stage == None:
            stage = AsyncPipelineStage()
        if len(self.stages):
            self.stages.insert(0, stage)
            self._set_output_callback(0)
        else:
            self.stages = [stage]

    def set_last_stage(self, stage):
        if len(self.stages):
            self.stages.append(stage)
            self._set_output_callback(-2)
        else:
            self.stages = [stage]

    def append_stages_and_callback(self, stages_and_callbacks):
        '''
        stages_and_callbacks是一个Iterable对象，其中元素为(stage, prestage_callback)
        '''
        for stage, callback in stages_and_callbacks:
            stage.set_prestage_callback(callback)
            self.set_last_stage(stage)

    async def aclose(self):
        for stage in self.stages:
            await stage.aclose()

    def close(self):   
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.aclose())
        if not loop.is_running():
            loop.run_until_complete(task)
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *execinfo):
        await self.aclose()

    def __enter__(self):
        return self
    
    def __exit__(self, *execinfo):
        self.close() 

    






















        


async def run_cmd_async(cmd, cwd = None):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd = cwd
        )

    stdout, stderr = await proc.communicate()
    return stdout, stderr

async def run_shellscript_async(shellscript, tmp_file, cwd = None):
    with open(tmp_file,'w') as fw:
        fw.write(shellscript)
    await run_cmd_async(tmp_file, cwd)




class DownloadManager(AsyncPipelineStage):
    def __init__(self, tasks = None, workers_num = 3):
        super().__init__(tasks, workers_num)

    async def git_clone(self, url, dst:Path, depth = 1):

        if depth == None:
            cmd = f'git clone {url}'
        else:
            cmd = f'git clone --depth={depth} {url}'
        