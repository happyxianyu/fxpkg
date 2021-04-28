import asyncio
import warnings

import more_itertools

from .async_queue import AsyncDeque


'''
后缀:
a: async，异步模式
b: 非异步模式
nw: no wait
'''



class AsyncPipelineStage:
    class RunningData:
        def __init__(self):
            self.uncomplete_num = 0
            self.out_q = AsyncDeque()
            self.done_event = asyncio.Event()
            self.next_stage = None

    class Command(BaseException):
        pass

    class Skip(Command):
        '''
        跳转命令，会将返回值放入该stage的结果队列
        如果跳转的为input stage，应当通知pipeline，when_task_done
        '''
        def __init__(self, stage):
            self.stage = stage
            self.res = None

    class Discard(Command):
        '''
        废弃结果，如果使用pipeline应当手动通知pipeline，when_task_done
        '''
        def __init__(self, pipe):
            self.pipe = pipe

    def __init__(self, tasks = None, workers_num = 3,
        in_callback = None, out_callback = None, 
        bind_stage = None, next_stage = None,
        scheduler = None):
        '''
        in_callback是push_data调用的协程，如果in_callback未定义，则push_data相关函数无效
        out_callback用于自动处理输出
        bind_stage为并联关系的stage，会将自身output设为对应stage的output
        next_stage为串联关系的stage，会设置out_callback为connector，将输出传递到下一个stage
        scheduler用于安排执行顺序
        '''
        self._in_q = AsyncDeque() #这里用deque是为了能够插队
        self.loop = asyncio.get_event_loop()

        self._running_data = self.RunningData()
        if bind_stage != None:
            self.set_bind_stage(bind_stage)
        if next_stage != None:
            self.set_next_stage(next_stage)

        self.set_in_callback(in_callback)
        self.set_out_callback(out_callback)
        self.set_scheduler(scheduler)

        if tasks!=None:
            self.put_tasks_nw(tasks)
        
        self.done_listeners = set()
        self.input_num = 0
        self.terminate_flag = False
        self.workers = [self.loop.create_task(self.worker()) for _ in range(workers_num)]

    async def worker(self):
        Skip = self.Skip
        Discard = self.Discard
        Command = self.Command
        while True:
            task = await self._get_inputs().popout()
            if self.terminate_flag:
                return

            e = None
            try:
                res = await task
            except Command as e1:
                e = e1
            except BaseException as e1:
                # 不可抛出异常，否则会终止整个pipeline
                self.handle_except(e1)

            self._when_task_done(res)

            if type(e) == Skip:
                await e.stage.put_out(e.res)
            elif type(e) == Discard:
                pass
            else:
                await self.put_out(res)

            running_data = self._running_data
            if running_data.uncomplete_num == 0:
                done_event = running_data.done_event
                if not done_event.is_set():
                    running_data.done_event.set()

    async def connector(self, res):
        if type(res) == self.Skip:
            e = res
            stage = e.stage
            res = e.res
        elif type(res) == self.Discard:
            stage = self
            while True:
                next_stage = stage.get_next_stage()
                if next_stage == None:
                    stage.out_callback(res)
                    return
        else:
            stage = self.get_next_stage()
        await stage.put_data(res)

    def handle_except(self, e):
        pass

    def _get_inputs(self):
        return self._in_q

    def get_outputs(self):
        return self._running_data.out_q

    def put_task_nw(self, task):
        self._when_put_task()
        self._get_inputs().put_nw(task)

    async def put_task(self, task):
        self._when_put_task()
        await self._get_inputs().put(task)

    def put_tasks_nw(self, tasks):
        for task in tasks:
            self.put_task_nw(task)

    async def put_tasks(self, tasks):
        for task in tasks:
            await self.put_task(task)

    def put_task_front_nw(self, task):
        self._when_put_task()
        self._get_inputs().appendleft_nw(task)

    async def put_task_front(self, task):
        self._when_put_task()
        await self._get_inputs().appendleft(task)

#put data:[
    def put_data_nw(self, data):
        if self.scheduler != None:
            self.loop.create_task(self.scheduler.schedule(data))
        else:
            self.put_task_nw(self.in_callback(data))

    async def put_data(self, data):
        if self.scheduler != None:
            await self.scheduler.schedule(data)
        else:
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
#put data:]

    async def put_task_node(self, node):
        '''
        
        '''
        loop = self.loop
        await self.put_task(self.in_callback(node))

    def put_task_node_nw(self, node):
        loop = self.loop
        if self.is_full():
            loop.create_task(self.put_task(self.in_callback(node)))
        else:
            self.put_task_nw(self.in_callback(node))

    async def put_out(self, res):
        '''
        若out_callback未定义，则将res送入输出队列
        '''
        out_callback = self.out_callback
        if out_callback == None:
            await self.get_outputs().put(res)
        else:
            await out_callback(res)

    def put_out_nw(self, res):
        out_callback = self.out_callback
        if out_callback == None:
            self.get_outputs().put_nw(res)
        else:
            self.loop.create_task(out_callback(res))

    def add_task_done_listener(self, f):
        self.done_listeners.add(f)

    def remove_task_done_listener(self, f):
        self.done_listeners.remove(f)

    def is_out_full(self):
        return self.get_outputs().is_full()

    def is_full(self):
        return self._in_q.is_full()

    def done(self):
        return self.get_uncomplete_num == 0

    def _when_put_task(self):
        running_data = self._running_data
        done_event = running_data.done_event
        if done_event.is_set():
            done_event.clear()
        running_data.uncomplete_num+=1
        self.input_num+=1
    
    def _when_task_done(self, res):
        self._running_data.uncomplete_num-=1
        for f in self.done_listeners:
            f(res)
    

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

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler
        if scheduler!=None:
            scheduler._set_stage(self)

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
    
    def connect(self, stage, callback = None):
        if callback!=None:
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
        ins = self._get_inputs()
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
        def _when_put_task():
            self.when_put_task()
            AsyncPipelineStage._when_put_task(stage)
        stage._when_put_task = _when_put_task

    def add_input_stages(self, stages):
        for stage in stages:
            self.add_input_stage(stage)

    def set_output_stage(self, stage):
        self.output_stage = stage
        async def out_callback(res):
            await stage.get_outputs().append(res)
            self.when_task_done()
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
        '''
        等待单个out
        '''
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
        '''
        等待全部out
        '''
        while not self.done():
            await self._done_event.wait()
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

    def when_put_task(self):
        '''
        当任务从非input stage输入时，应当调用此方法
        '''
        self.uncomplete_num+=1
        done_event = self._done_event
        if done_event.is_set():
            done_event.clear()

    def when_task_done(self):
        '''
        当任务从非output stage离开管线时，应当调用此方法
        '''
        self.uncomplete_num-=1
        if self.done():
            done_event = self._done_event
            if not done_event.is_set():
                done_event.set()
            self.loop.create_task(self.get_outputs().force_pop_no_wait()) #考虑到discard，已完成任务，避免阻塞

    async def __aenter__(self):
        return self

    async def __aexit__(self, *execinfo):
        await self.close()

    def __enter__(self):
        return self
    
    def __exit__(self, *execinfo):
        self.close_b()
    


class TaskNode:
    '''
    需要可hash，可比较相等
    每次使用应当重新构造新的dag
    需要考虑实现copy, __eq__, __hash__
    '''
    def __init__(self, succs = None, weight = 1):
        self.succs = set()
        self.indegree = 0
        self.scheduled = False

        self.weight = weight #表示该节点开销，开销小的会被先执行

        self._copied = None
        if succs != None:
            self.add_succs(succs)

    def is_source(self):
        return self.indegree == 0

    def is_sink(self):
        return len(self.succs) == 0

    def add_succ(self, succ):
        succ.indegree+=1
        self.succs.add(succ)

    def add_succs(self, succs):
        map(self.add_succ, succs)

    def __hash__(self):
        return id(self)

    def __eq__(self, x):
        return id(self) == id(x)

    def copy(self):
        '''
        用于拷贝用户自定义属性
        '''
        res = TaskNode()
        res.weight = self.weight
        return res

    def _copy_recursive(self):
        if self._copied != None:
            return self._copied
        self._copied = self.copy()
        succs = [succ._copy_recursive() for succ in self.succs]
        self._copied.add_succs(succs)
        return self._copied

    @staticmethod
    def copy_dag(sources):
        '''
        如果要taskscheduler自动构造实例，该函数在使用scheduler之前要调用一次
        '''
        return [source._copy_recursive() for source in sources]

    @staticmethod
    def topo_sort_dag(sources):
        visited = set()
        post_list = []
        
        def dfs(x):
            if x in visited:
                return
            visited.add(x)
            succs = sorted(x.succs, key=lambda x:x.weight)
            for succ in succs:
                dfs(succ)
            post_list.append(x)

        for n in sources:
            dfs(n)
        post_list.reverse()
        return post_list
    
        


class TaskScheduler:
    '''
    基于DAG的任务规划器
    规划器只对于put_data有效
    '''
    def __init__(self, done_stage = None, not_copied_warn = True):
        '''
        stage为任务开始的stage
        done_stage为任务结束的stage，如果done_stage未设置，应当手动调用when_done
        '''
        self.stage = None
        if done_stage == None:
            self.done_stage = None
        else:
            self.set_done_stage(done_stage)
        self._not_copied_warn = not_copied_warn

    async def schedule(self, node:TaskNode):
        '''
        安排任务，表示node的上一阶段stage已经完成
        node不可被两个scheduler复用
        '''
        stage = self.stage
        node.scheduled = True   
        if node.indegree == 0:
            await stage.put_task_node(node)

    def when_done(self, node:TaskNode):
        '''
        node完成，后继节点可以被stage执行
        该函数可以不在当前stage被回调
        '''
        stage = self.stage
        for succ in node.succs:
            succ.indegree -= 1
            if succ.indegree == 0 and succ.scheduled:
                stage.put_task_node_nw(succ)    #避免死锁
        if node._copied != None:
            return node._copied
        else:
            if self._not_copied_warn:
                warnings.warn('TaskNode is not copied!!!')
            return node
    
    def close(self):
        if self.done_stage!=None:
            self.done_stage.remove_task_done_listener(self.when_done)

    def _set_stage(self, stage):
        self.stage = stage

    def set_done_stage(self, stage):
        self.close()
        self.done_stage = stage
        stage.add_task_done_listener(self.when_done)


