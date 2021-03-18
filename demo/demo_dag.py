import mimesis
from pprint import pprint
from collections import deque


class InstallDAGNode:
    def __init__(self, installer, succs:list):
        self.indegree = 0
        self.installer = installer
        self.configInfo = installer.configurer.configInfo
        self.identifier = None #TODO
        self._hashcode = hash(self.identifier)
        if succs == None:
            succs = []
        self.succs = succs
        for node in self.succs:
            node.indegree += 1

    def remove(self):
        for node in self.succs:
            node.indegree -= 1
        node.succs = []
        
    def add_succ(self, succ):
        self.succs.append(succ)
        succ.indegree += 1

    def set_downloaded(self):
        self.downloaded_flag = True

    def downloaded(self):
        return self.downloaded_flag

    def __hash__(self):
        return self._hashcode

    def __eq__(self, x):
        return self.identifier == x.identifier

    
class InstallDAG:
    def __init__(self, sources):
        self.sources = set()
        self.wait_q = deque()
        for node in self.sources:
            if node.downloaded():
                self.wait_q.append(node)
            else:
                self.sources.add(node)
    
    def add_downloaded(self, node):
        if node in self.sources:
            self.sources.remove(node)
            self.wait_q.append(node)

    def fetch_nodes(self):
        wait_q = self.wait_q
        while len(wait_q):
            node = wait_q.popleft()
            yield node
            succs = node.succs
            node.remove()
            for succ in node.succs:
                if succ.indegree == 0:
                    if succ.downloaded():
                        wait_q.append(succ)
                    else:
                        self.sources.add(succ)
    