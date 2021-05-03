# -*- coding:utf-8 -*-
import logging
from fxpkg.util import Path
from .manager import *


__all__ = [
    'setup_fxpkg',
    'Host'
]

def setup_fxpkg(path, is_prefix = True):
    '''
    若is_prefix == False， 则在path创建程序本体
    若is_prefix == True，则在path/fxpkg创建程序本体
    成功返回Host
    '''
    path = Path(path)
    if is_prefix:
        root_path = path/'fxpkg'
    else:
        root_path = path
    return Host(root_path)


class Host:
    def __init__(self, root_path):
        self.pathManager = PathManager(root_path)
        self.configManager = ConfigManager(self.pathManager)
        self.libManager = LibManager(self.pathManager, self.configManager)




    
