import logging
import random
import asyncio

import networkx as nx
import matplotlib.pyplot as plt

from fxpkg.util.async_pipeline import *

g_seed = 7329
random.seed(g_seed)


print = logging.debug
async def foo(n):
    print('Waiting: ', n)
    await asyncio.sleep(n)
    print('Completing: ', n)
    return n

def stage_callback_foo(i, n):
    async def callback(res):
        print(f'stage: {i}; pre_res: {res}; Waiting: {n}')
        await asyncio.sleep(n)
        print(f'stage: {i}; completing: {n}')
        return i,n
    return callback

def test_pipe_run():
    pipe = AsyncPipeline()
    pipe.add_serial_stages(
        [AsyncPipelineStage(workers_num=3, in_callback = stage_callback_foo(i, (i+1)/10)) for i in range(5)]
    )
    for i in range(10):
        pipe.get_input_stage().put_data_nw(i)

    for res in pipe.run_b():
        print(f'Final result: {res}')
    pipe.close_b()

def test_pipe_wait_done():
    pipe = AsyncPipeline()
    pipe.add_serial_stages(
        [AsyncPipelineStage(workers_num=3, in_callback = stage_callback_foo(i, i/10)) for i in range(5)]
    )
    for i in range(10):
        pipe.get_input_stage().put_data_nw(i)

    pipe.wait_done_b()

    for res in pipe.get_outputs():
        print(f'Final result: {res}')
    pipe.close_b()


def test_scheduler():
    def stage_callback_foo(i):
        async def callback(n):
            print(f'stage: {i}; Waiting: {n}')
            await asyncio.sleep(n.v)
            print(f'stage: {i}; completing: {n}')
            return n
        return callback

    class TestNode(TaskNode):
        def __init__(self, v):
            self.v = v
            super().__init__()

        def __str__(self):
            return str(self.v)

        def copy(self):
            res = super().copy()
            res.v = self.v
            return res

    def show_graph(g):
        nx.draw(g, with_labels = True, pos = nx.spring_layout(g, seed = g_seed))
        plt.show()
    
    def random_connect(nodes):
        nodes = list(nodes)
        g = nx.DiGraph()
        def connect(a, b):
            nodes[a].add_succ(nodes[b])
            g.add_edge(a, b)

        for length in range(1, len(nodes)):
            p = 1/(length+1)
            for a in range(len(nodes)-length):
                b = a+length
                if random.random() < p:
                    connect(a, b)
        assert(nx.is_directed_acyclic_graph(g))
        return g

    nodes = [TestNode((i+1)/10) for i in range(20)]

    TaskNode.copy_dag(filter(TaskNode.is_source, nodes))
    random.shuffle(nodes)

    g = random_connect(nodes)
    
    nodes = TaskNode.topo_sort_dag([n for n in nodes if n.is_source()])
    
    stages =[AsyncPipelineStage(in_callback=stage_callback_foo(i+1), workers_num = 7) for i in range(5)]
    pipe = AsyncPipeline()
    pipe.add_serial_stages(stages)

    scheduler = TaskScheduler()
    stages[0].put_datas_nw(nodes)
    stages[1].set_scheduler(scheduler)
    scheduler.set_done_stage(stages[3])
    pipe.wait_done_b()
    # pipe.close_b()    #Testing cleanup
