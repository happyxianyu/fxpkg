# -*- coding:utf-8 -*-
import logging
import dataclasses
import typing

import sqlalchemy as sa
from sqlalchemy import Table, Column, Index, Integer, BLOB, Text, Enum
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import CursorResult

from fxpkg.common.constants import InstallState
from fxpkg.common.dataclass import InstallEntry
from fxpkg.util import Path

from .util import SaDb
from .types import PickleType, PathType

__all__ = ['InstallEntryTable', 'InstallInfoRepository']


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

    def __init__(self, db: SaDb):
        self.db = db
        self.tb = Table(
            'InstallEntry_tb', db.metadata,
            Column('entry_id', Integer, primary_key=True),

            Column('libid', Text, index=True),  # libid不可以以'main.'开头
            Column('version', Text),
            Column('compiler', Text, default=''),
            Column('platform', Text, default=''),
            Column('arch', Text, default=''),
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

    def get_by_entry_id(self, entry_id: int) -> InstallEntry:
        return self._search_one(dict(entry_id=entry_id))

    def get_by_key_fields(self, entry: InstallEntry, exact=True) -> InstallEntry:
        """
        get 只返回一个结果
        libid是必须的
        对于有默认值的field，如果对应的值为None，则视为''
        只有key field有效，value field会被忽略
        若exact = False，则可以匹配除了值本身外，还可以匹配''
        """
        assert entry.libid is not None
        key_fields = self.key_fields
        entry_d = self._entry_to_dict(entry)
        keys = {k: entry_d.get(k, '') for k in key_fields}
        if exact:
            return self._search_one(keys)
        else:
            founds = self._find_by_libid(entry.libid)
            return InstallEntry(**self._get_best_matched(founds, entry_d))

    def find_by_key_fields(self, entry: InstallEntry, exact=True) -> typing.List[InstallEntry]:
        """
        会按照version进行降序排序
        若exact为False，则会先搜索最佳匹配，然后再照最佳匹配进行查询
        libid是必须的
        """
        assert entry.libid is not None
        key_fields = self.key_fields
        entry_d = self._entry_to_dict(entry)
        keys = {k: entry_d[k] for k in key_fields if entry_d[k] is not None}

        if exact:
            founds = self._search(keys).all()
            return [InstallEntry(**found) for found in founds]
        else:
            founds = self._find_by_libid(entry.libid)
            best_matched = self._get_best_matched(founds, keys)  # 用于决定都有哪些field
            if best_matched is None:
                return []
            results = [InstallEntry(**found) for found in founds if all(best_matched[k] == found[k] for k in keys)]
            return results

    def _get_best_matched(self, founds, entry_d: dict):
        if len(founds) == 0:
            return

        key_fields = self.key_fields
        best_match = None
        for found in founds:
            perfect_match = True
            better_matched = False
            for k in key_fields:
                if entry_d[k] is None:  # None 用于匹配任意
                    continue
                if found[k] == entry_d[k]:  # 精确匹配
                    if str(best_match[k]) == '':
                        better_matched = True
                elif str(found[k]) == '':  # 非精确
                    perfect_match = False
                else:  # 匹配失败
                    better_matched = False
                    break

            if better_matched:
                best_match = found
            if perfect_match:
                best_match = found
                break
        return best_match

    def _find_by_libid(self, libid: str) -> list:
        assert libid is not None
        ress = self._search({'libid': libid})
        return ress.all()

    def _search(self, keys: dict, order_by: list = None, desc=True) -> CursorResult:
        conn = self.db.conn
        tb = self.tb
        stmt = tb.select().where(*(tb.c[k] == keys[k] for k in keys.keys()))
        if order_by is not None:
            if desc:
                stmt = stmt.order_by(*(tb.c[term].desc() for term in order_by))
            else:
                stmt = stmt.order_by(*(tb.c[term] for term in order_by))
        ress = conn.execute(stmt)
        return ress

    def _search_one(self, keys: dict) -> InstallEntry:
        ress = self._search(keys)
        res = ress.fetchone()
        if res is None:
            return None
        entry = self._dict_to_entry(res)
        return entry

    def update_entry_by_entry_id(self, entry: InstallEntry):
        conn = self.db.conn
        tb = self.tb
        entry_id = entry.entry_id
        entry_d = self._entry_to_dict(entry)

        entry_request = self.get_by_entry_id(entry_id)
        if entry_request is None:
            stmt = tb.insert().values(**entry_d)
        else:
            del entry_d['entry_id']
            stmt = tb.update().where(entry_id=entry_id).values(**entry_d)
        self._exec(stmt)

    def update_entry_by_key_fields(self, entry: InstallEntry):
        """
        要求key fields全部填满
        """
        assert all(hasattr(entry, attr) for attr in self.key_fields)
        conn = self.db.conn
        tb = self.tb
        entry_d = self._entry_to_dict(entry)
        if 'entry_id' in entry_d:
            del entry_d['entry_id']
        keys = {k: entry_d[k] for k in self.key_fields}
        vals = {k: entry_d[k] for k in self.val_fields}

        entry_request = self._search_one(keys)
        if entry_request is None:
            stmt = tb.insert().values(**entry_d)
        else:
            stmt = tb.update().where(**keys).values(**vals)
        self._exec(stmt)

    def _exec(self, *stmts):
        conn = self.db.conn
        for stmt in stmts:
            try:
                with conn.begin():
                    conn.execute(stmt)
            except SQLAlchemyError:
                return False
        return True


class InstallInfoRepository:
    def __init__(self, path=':memory:', echo=False):
        if path != ':memory:':
            Path(path).prnt.mkdir()
        url = 'sqlite:///' + str(path)
        db = SaDb(url, echo=echo)
        self._db = db
        self._installEntry_tb = InstallEntryTable(db)
        db.create_tables()

    def get_by_entry_id(self, entry_id: int) -> InstallEntry:
        return self._installEntry_tb.get_by_entry_id(entry_id)

    def get_by_key_fields(self, entry: InstallEntry, exact=True) -> InstallEntry:
        """
        get 只返回一个结果
        libid是必须的
        对于有默认值的field，如果对应的值为None，则视为''
        只有key field有效，value field会被忽略
        若exact = False，则可以匹配除了值本身外，还可以匹配''
        """
        return self._installEntry_tb.get_by_key_fields(entry, exact)

    def find_by_key_fields(self, entry: InstallEntry, exact=True) -> typing.List[InstallEntry]:
        """
        会按照version进行降序排序
        若exact为False，则会先搜索最佳匹配，然后再照最佳匹配进行查询
        libid是必须的
        """
        return self._installEntry_tb.find_by_key_fields(entry, exact)

    def update_entry_by_entry_id(self, entry: InstallEntry):
        return self._installEntry_tb.update_entry_by_entry_id(entry)

    def update_entry_by_key_fields(self, entry: InstallEntry):
        """
        要求key fields全部填满
        """
        return self._installEntry_tb.update_entry_by_key_fields(entry)