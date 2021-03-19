import asyncio

class TaskNode:
    '''
    需要可hash，可比较相等
    '''
    def __init__(self, succs = None):
        self.succs = []
        self.indegree = 0
        self.orig_indegree = 0
        self.scheduled = False
        if succs != None:
            self.add_succs(succs)

    def add_succ(self, succ):
        self.orig_indegree+=1
        succ.indegree+=1
        self.succs.append(succ)

    def add_succs(self, succs):
        map(self.add_succ, succs)

    def restore_state(self):
        '''
        重置indegree, 已安排标志
        '''
        self.indegree = self.orig_indegree
        self.scheduled = False

    def __hash__(self):
        return id(self)

    def __eq__(self, x):
        return id(self) == id(x)


class TaskScheduler:
    '''
    基于DAG的任务规划器
    '''
    def __init__(self, stage = None):
        self.loop = asyncio.get_event_loop()
        #TODO

    async def schedule(self, node:TaskNode):
        '''
        安排任务，表示该节点的上一阶段stage已经完成
        '''
        node.scheduled = True
        if node.indegree == 0:
            await self.put_data(node)

    def when_done(self, node:TaskNode):
        '''
        某一节点完成
        '''
        loop = self.loop
        for succ in node.succs:
            succ.indegree -= 1
            if succ.indegree == 0 and succ.scheduled:
                if self.is_full():
                    loop.create_task(self.put_data(succ))   #避免死锁
                else:
                    self.put_data_nw(succ)
        node.restore_state()    #应当恢复状态便于下一阶段复用

    def put_data_nw(self, data):
        '''
        绑定到stage时该函数会被替换为当前stage的方法
        '''
        pass

    async def put_data(self, data):
        '''
        绑定到stage时该函数会被替换为当前stage的方法
        '''
        pass

    def is_full(self):
        '''
        绑定到stage时该函数会被替换为当前stage的方法
        '''
        pass