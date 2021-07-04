

class DAGNode:
    '''
        需要可hash，可比较相等
        每次使用应当重新构造新的dag
        需要考虑实现copy, __eq__, __hash__
        '''

    def __init__(self, succs=None, weight=1):
        self.succs = set()
        self.indegree = 0
        self.scheduled = False

        self.weight = weight  # 表示该节点开销，开销小的会被先执行

        self._copied = None
        if succs != None:
            self.add_succs(succs)

    def is_source(self):
        return self.indegree == 0

    def is_sink(self):
        return len(self.succs) == 0

    def add_succ(self, succ):
        succ.indegree += 1
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
        res = type(self)()
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
            succs = sorted(x.succs, key=lambda x: x.weight)
            for succ in succs:
                dfs(succ)
            post_list.append(x)

        for n in sources:
            dfs(n)
        post_list.reverse()
        return post_list



class DiDAGNode:
    def __init__(self):
        self.succs = set()
        self.prevs = set()
        self.weight = 1  # 表示该节点开销，开销小的会被先执行
        self._copied = None # 用于拷贝节点时使用

    @property
    def indegree(self):
        return len(self.prevs)

    @property
    def outdegree(self):
        return len(self.succs)

    def is_source(self):
        return self.indegree == 0

    def is_sink(self):
        return len(self.succs) == 0

    def add_succ(self, succ: 'DiDAGNode'):
        succ.prevs.add(self)
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
        res = DiDAGNode()
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
        return [source._copy_recursive() for source in sources]

    @staticmethod
    def topo_sort_dag(sources):
        visited = set()
        post_list = []

        def dfs(x):
            if x in visited:
                return
            visited.add(x)
            succs = sorted(x.succs, key=lambda x: x.weight)
            for succ in succs:
                dfs(succ)
            post_list.append(x)

        for n in sources:
            dfs(n)
        post_list.reverse()
        return post_list

class DiDAG:
    def __init__(self, sources):
        self.sources = set(sources)

    def copy(self):
        DiDAGNode.copy_dag(self.sources)

