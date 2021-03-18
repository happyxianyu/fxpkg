import asyncio
import more_itertools
from .async_queue import AsyncDeque


'''
后缀:
b: block
nw: no wait
'''



class AsyncPipelineStage:
    class RunningData:
        def __init__(self):
            self.uncomplete_num = 0
            self.out_q = AsyncDeque()
            self.done_event = asyncio.Event()
            self.next_stage = None

    class Skip(BaseException):
        '''
        跳转命令，可以将结果传送到之后的某个stage，但不可传递到之前的stage
        '''
        def __init__(self, stage = None):
            self.stage = stage
            self.res = None

    class Discard(BaseException):
        '''
        废弃结果
        '''
        def __init__(self):
            self.res = None

    def __init__(self, tasks = None, workers_num = 3,in_callback = None, out_callback = None, 
        bind_stage = None, next_stage = None):
        self._in_q = AsyncDeque()
        self.loop = asyncio.get_event_loop()

        self._running_data = self.RunningData()
        if bind_stage != None:
            self.set_bind_stage(bind_stage)
        if next_stage != None:
            self.set_next_stage(next_stage)

        self.set_in_callback(in_callback)
        self.set_out_callback(out_callback)

        if tasks!=None:
            self.put_tasks_nw(tasks)
        
        self.input_num = 0
        self.terminate_flag = False
        self.workers = [self.loop.create_task(self.worker()) for _ in range(workers_num)]

    async def worker(self):
        while True:
            task = await self.get_inputs().popout()
            if self.terminate_flag:
                return

            try:
                res = await task
            except:
                pass

            self._when_complete_task(self)

            out_callback = self.out_callback
            if out_callback == None:
                await self.get_outputs().put(res)
            else:
                callback_res = await out_callback(res)

            running_data = self._running_data
            if running_data.uncomplete_num == 0:
                done_event = running_data.done_event
                if not done_event.is_set():
                    running_data.done_event.set()

    async def connector(self, res):
        if type(res) == self.Skip:
            e = res
            stage = e.next_stage
            res = e.res
        elif type(res) == self.Discard:
            stage = self
            while True:
                next_stage = stage.get_next_stage()
                if next_stage == None:
                    stage.out_callback(res)
                    return
            return
        else:
            stage = self.get_next_stage()
        await stage.put_data(res)

    def get_inputs(self):
        return self._in_q

    def get_outputs(self):
        return self._running_data.out_q

    def put_task_nw(self, task):
        self._when_put_task(self)
        self.get_inputs().put_nw(task)

    async def put_task(self, task):
        self._when_put_task(self)
        await self.get_inputs().put(task)

    def put_tasks_nw(self, tasks):
        for task in tasks:
            self.put_task_nw(task)

    async def put_tasks(self, tasks):
        for task in tasks:
            await self.put_task(task)

    def put_task_front_nw(self, task):
        self._when_put_task(self)
        self.get_inputs().appendleft_nw(task)

    async def put_task_front(self, task):
        self._when_put_task(self)
        await self.get_inputs().appendleft(task)

    def put_data_nw(self, data):
        self.put_task_nw(self.in_callback(data))

    async def put_data(self, data):
        await self.put_task(self.in_callback(data))

    def put_datas_nw(self, datas):
        for data in datas:
            self.put_data_nw(data)
    
    async def put_datas(self, datas):
        for data in datas:
            await self.put_data(data)

    def put_data_front_nw(self, data):
        self.put_task_front_nw(self.in_callback(data))

    async def put_data_front(self, data):
        await self.put_task_front(self.in_callback(data))

    def put_datas_front_nw(self, datas):
        for data in datas:
            self.put_data_front_nw(data)

    async def put_datas_front(self, datas):
        for data in datas:
            await self.put_data_front(data)

    @staticmethod
    def _when_put_task(self):
        running_data = self._running_data
        done_event = running_data.done_event
        if done_event.is_set():
            done_event.clear()
        running_data.uncomplete_num+=1
        self.input_num+=1

    @staticmethod
    def _when_complete_task(self):
        self._running_data.uncomplete_num-=1
    

    def wait_b(self):
        '''
        若存在任务未完成，返回True，否则返回False
        '''
        if not self.done():
            self.get_outputs.wait_b()
            return True
        return False

    async def wait(self):
        if not self.done():
            await self.get_outputs.wait()
            return True
        return False

    def wait_done_b(self):
        if not self.done():
            self.loop.run_until_complete(
                self._running_data.done_event.wait())

    async def wait_done(self):
        if not self.done():
            await self._running_data.done_event.wait()

    def run_b(self):
        while self.wait():
            outs = self.get_outputs()
            while len(outs):
                yield outs.popout_nw()

    async def run(self):
        while await self.wait():
            outs = self.get_outputs()
            while len(outs):
                yield outs.popout_nw()
    
    def get_uncomplete_num(self):
        return self._running_data.uncomplete_num
    
    def get_next_stage(self):
        return self._running_data.next_stage

    def done(self):
        return self.get_uncomplete_num == 0

    def set_out_callback(self, callback):
        '''
        设置处理输出的协程，当该设置该callback时，输出队列将被忽略
        '''
        self.out_callback = callback
        return self

    def set_in_callback(self, callback):
        '''
        设置处理put_data的协程
        '''
        self.in_callback = callback
        return self

    def set_bind_stage(self, stage):
        '''
        并联关系的stage，统一处理结果
        将自身的outputs设为stage的outputs
        '''
        self.bind_stage = stage
        self._running_data = stage._running_data

    def set_next_stage(self, stage):
        '''
        串联关系的stage，结果传递到下一个stage
        设置输出队列为下一stage的输入队列
        会设置该stage的out_callback为connector
        要求下一stage必须设置了in_callback
        '''
        self._running_data.next_stage = stage
        self.set_out_callback(self.connector)
        self._running_data.out_q = stage._in_q
        return stage

    def set_next_stages(self, stages, in_callbacks = None):
        cur = self
        if in_callbacks == None:
            for stage in stages:
                cur.set_next_stage(stage)
                cur = stage
        else:
            for stage, callback in zip(stages, in_callbacks):
                stage.set_in_callback(callback)
                cur.set_next_stages(stage)
                cur = stage
        return cur

    def bind_from(self, stages):
        for stage in stages:
            stage.set_bind_stage(self)
        return self
    
    def connect(self, stage, callback):
        stage.set_in_callback(callback)
        self.set_next_stage(stage)
        return stage

    def closed(self):
        return len(self.workers) == 0

    async def close(self):
        workers = self.workers
        if self.closed():
            return False
        self.terminate_flag = True
        ins = self.get_inputs()
        num = len(workers) - len(ins)
        if num>0:
            for _ in range(num):
                await ins.put(None)
        for worker in workers:
            await worker
        self.workers = []
        return True
    
    def close_b(self):
        workers = self.workers
        if self.closed():
            return False

        loop = self.loop
        task = loop.create_task(self.close())
        if not loop.is_running():
            loop.run_until_complete(task)
        return True

    async def close_recursive(self, until_closed = True):
        if until_closed and self.closed():
            return False

        await self.close()
        next_stage = self.get_next_stage()
        if next_stage == None:
            return
        await next_stage.close_recursive(until_closed)
        return True

    def close_recursive_b(self, until_closed = True):
        if until_closed and self.closed():
            return False

        loop = self.loop
        task = loop.create_task(self.close_recursive())
        if not loop.is_running():
            loop.run_until_complete(task)
        return True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *execinfo):
        await self.close()

    def __enter__(self):
        return self
    
    def __exit__(self, *execinfo):
        self.close_b() 



class AsyncPipeline:
    def __init__(self, input_stages = None, output_stage:AsyncPipelineStage = None):
        if input_stages == None:
            stages = input_stages
        elif type(input_stages) != list:
            input_stages = list(input_stages)

        self._done_event = asyncio.Event()
        if input_stages == None:
            input_stages = []
        self.input_stages = input_stages
        self.output_stage = output_stage
        self.uncomplete_num = 0
        self.loop = asyncio.get_event_loop()

    def add_input_stage(self, stage):
        self.input_stages.append(stage)
        def _when_put_task(stage):
            self.uncomplete_num+=1
            done_event = self._done_event
            if done_event.is_set():
                done_event.clear()
            AsyncPipelineStage._when_put_task(stage)
        stage._when_put_task = _when_put_task

    def add_input_stages(self, stages):
        for stage in stages:
            self.add_input_stage(stage)

    def set_output_stage(self, stage):
        self.output_stage = stage
        # def _when_complete_task(stage):
        #     self.uncomplete_num-=1
        #     done_event = self._done_event
        #     if not done_event.is_set():
        #         done_event.set()
        #     AsyncPipelineStage._when_complete_task(stage)
        # stage._when_complete_task = _when_complete_task

        async def out_callback(res):
            self.uncomplete_num-=1
            if type(res) == AsyncPipelineStage.Discard:
                pass
            else:
                await stage.get_outputs().put(res)
            if self.done():
                done_event = self._done_event
                if not done_event.is_set():
                    done_event.set()
        stage.set_out_callback(out_callback)

    def add_serial_stages(self, stages, as_output = True):
        stages = iter(stages)
        stage1 = more_itertools.first(stages)
        self.add_input_stage(stage1)
        last_stage = stage1.set_next_stages(stages)
        if as_output:
            self.set_output_stage(last_stage)
        return last_stage

    def done(self):
        return self.uncomplete_num == 0

    def get_input_stage(self):
        return self.input_stages[0]

    def get_outputs(self):
        return self.output_stage.get_outputs()

    async def wait(self):
        if not self.done():
            await self.get_outputs().wait()
            return True
        return False

    def wait_b(self):
        if not self.done():
            self.loop.run_until_complete(self.get_outputs().wait())
            return True
        return False

    async def wait_done(self):
        if not self.done():
            await self._done_event.wait()
            if not self.done():
                await self.get_outputs().wait()
            return True
        return False
    
    def wait_done_b(self):
        if not self.done():
            return self.loop.run_until_complete(self.wait_done())
        return False
        
    async def run(self):
        while await self.wait():
            outs = self.get_outputs()
            while(len(outs)):
                yield outs.popout_nw()

    def run_b(self):
        while self.wait_b():
            outs = self.get_outputs()
            while(len(outs)):
                yield outs.popout_nw()

    def closed(self):
        if self.output_stage == None:
            return False
        return self.output_stage.closed()

    async def close(self):
        if self.closed():
            return False
        for stage in self.input_stages:
            await stage.close_recursive()
        return True

    def close_b(self):
        if self.closed():
            return False
        loop = self.loop
        task = loop.create_task(self.close())
        if not loop.is_running():
            loop.run_until_complete(task)
        return True

    async def __aenter__(self):
        return self

    async def __aexit__(self, *execinfo):
        await self.close()

    def __enter__(self):
        return self
    
    def __exit__(self, *execinfo):
        self.close_b()
    