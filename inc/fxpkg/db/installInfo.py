# -*- coding:utf-8 -*-
import logging

import dataclasses

import sqlalchemy as sa
from sqlalchemy import Table, Column, Index, Integer, BLOB, Text, Enum
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from fxpkg.common.constants import InstallState
from fxpkg.common.dataclass import InstallEntry
from fxpkg.util import Path

from .util import SaDb
from .types import PickleType, PathType


class InstallEntryTable:
    key_fields = ['libid', 'version', 'compiler', 'platform', 'arch', 'build_type', 'other_key']
    val_fields = [
        'install_path', 'include_path', 'lib_path', 'bin_path', 'cmake_path',
        'lib_list', 'dll_list',
        'dependent', 'dependency',
        'install_state',
        'other'
    ]

    fields = key_fields + val_fields
    all_fields = ['entry_id'] + fields

    def __init__(self, repo: 'InstallInfoRespository'):
        self.repo = repo
        self.tb = Table(
            'InstallEntry_tb', repo.metadata,
            Column('entry_id', Integer, primary_key=True),

            Column('libid', Text, index=True),
            Column('version', Text),
            Column('compiler', Text, default=''),
            Column('platform', Text, default= ''),
            Column('arch', Text, default = ''),
            Column('build_type', Text, default=''),
            Column('other_key', PickleType, default=''),

            Column('install_path', PathType),
            Column('include_path', PathType, default=''),
            Column('lib_path', PathType, default=''),
            Column('bin_path', PathType, default=''),
            Column('cmake_path', PathType, default=''),

            Column('lib_list', PickleType, default=''),
            Column('dll_list', PickleType, default=''),

            Column('dependent', PickleType, default=''),
            Column('dependency', PickleType, default=''),

            Column('install_state', Enum(InstallState)),

            Column('other', PickleType, default=''),
            UniqueConstraint(*self.key_fields)
        )

    @staticmethod
    def _entry_to_dict(entry: InstallEntry) -> dict:
        return dataclasses.asdict(entry)

    @staticmethod
    def _dict_to_entry(d) -> InstallEntry:
        return InstallEntry(**d)

    def get_by_entry_id(self, entry_id: int):
        return self._search_one(dict(entry_id=entry_id))

    def get_by_key_fields(self, entry: InstallEntry, exact = True):
        """
        要求key fields全部填满, 只有key field有效，value field会被忽略
        若exact = False，则可以匹配除了值本身外，还可以匹配''
        """
        key_fields = self.key_fields
        entry_d = self._entry_to_dict(entry)
        if exact:
            keys = {k: entry_d[k] for k in key_fields}
            return self._search_one(keys)
        else:
            pass#TODO

    def _search(self, keys: dict):
        conn = self.repo.conn
        tb = self.tb
        stmt = tb.select().where(*(tb.c[k] == keys[k] for k in keys.keys()))
        ress = conn.execute(stmt)
        return ress

    def _search_one(self, keys: dict):
        ress = self._search(keys)
        res = ress.fetchone()
        if res is None:
            return None
        entry = self._dict_to_entry(res)
        return entry

    def update_entry_by_entry_id(self, entry: InstallEntry):
        conn = self.repo.conn
        tb = self.tb
        entry_id = entry.entry_id
        entry_d = self._entry_to_dict(entry)

        entry_request = self.get_by_entry_id(entry_id)
        if entry_request is None:
            stmt = tb.insert().values(**entry_d)
        else:
            del entry_d['entry_id']
            stmt = tb.update().where(entry_id=entry_id).values(**entry_d)
        return self._exec(stmt)

    def update_entry_by_key_fields(self, entry: InstallEntry):
        '''
        要求key fields全部填满
        '''
        assert all(hasattr(entry, attr) for attr in self.key_fields)
        conn = self.repo.conn
        tb = self.tb
        entry_d = self._entry_to_dict(entry)
        if 'entry_id' in entry_d:
            del entry_d['entry_id']
        keys = {k:entry_d[k] for k in self.key_fields}
        vals = {k:entry_d[k] for k in self.val_fields}

        entry_request = self._search_one(keys)
        if entry_request is None:
            stmt = tb.insert().values(**entry_d)
        else:
            stmt = tb.update().where(**keys).values(**vals)
        return self._exec(stmt)

    def _exec(self, *stmts):
        conn = self.repo.conn
        for stmt in stmts:
            try:
                with conn.begin():
                    conn.execute(stmt)
            except SQLAlchemyError:
                return False
        return True

class InstallInfoRespository:
    def __init__(self, path=':memory:', echo=False):
        if path != ':memory:':
            Path(path).prnt.mkdir()
        url = 'sqlite:///' + str(path)
        self.db = SaDb(url, echo=echo)
        self.conn = self.db.connect()
        self.metadata = self.db.metadata
        self.installEntry_tb = InstallEntryTable(self)
        self.create_tables()

    def create_tables(self):
        self.db.metadata.create_all()


__all__ = ['InstallEntryTable', 'InstallInfoRespository']
