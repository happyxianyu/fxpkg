# -*- coding:utf-8 -*-
import more_itertools

import sqlalchemy as sa
from sqlalchemy import Table, Column, Index, Integer, BLOB, Text, Enum
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy import select


from fxpkg.common.constants import InstallState
from fxpkg.util.path import Path

from .util import SaDb
from .types import PickleType


class InstallEntryTable:
    key_fields = ['libid', 'version', 'compiler', 'platform', 'arch', 'build_type', 'other_keys']
    val_fields = [
        'install_path', 'include_path', 'lib_path', 'bin_path', 'cmake_path',
        'lib_list', 'dll_list',
        'dependent','dependency',
        'install_state',
        'other'
    ]
    
    fields = key_fields + val_fields
    all_fields = ['entry_id'] + fields

    def __init__(self, repo):
        self.repo = repo
        self.tb = Table(
            'InstallEntry_tb', repo.metadata,
            Column('entry_id', Integer, primary_key = True),

            Column('libid', Text, index = True),
            Column('version', Text),
            Column('compiler', Text),
            Column('platform', Text),
            Column('arch', Text),
            Column('build_type', Text),
            Column('other_keys', PickleType),

            Column('install_path', Text),
            Column('include_path', Text),
            Column('lib_path', Text),
            Column('bin_path', Text),
            Column('cmake_path', Text),

            Column('dependent', PickleType),
            Column('dependency', PickleType),

            Column('install_state', Enum(InstallState)),
            Column('other', PickleType, server_default = ""),
            UniqueConstraint(*self.key_fields)
        )


    def get_by_id(self, id, fields = None):
        pass


class InstallInfoRespository:
    def __init__(self, path = ':memory:', echo = False):
        if path != ':memory:':
            Path(path).prnt.mkdir()
        url = 'sqlite:///' + str(path)
        self.db = SaDb(url, echo = echo)
        self.conn = self.db.connect()
        self.metadata = self.db.metadata
        self.installEntry_tb = InstallEntryTable(self)
        self.create_tables()

    def create_tables(self):
        self.db.metadata.create_all()


__all__ = ['InstallEntryTable', 'InstallInfoRespository']