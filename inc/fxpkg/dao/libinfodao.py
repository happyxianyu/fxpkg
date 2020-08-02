from fxpkg.model import LibInfo
from sqlalchemy.sql import expression as sqlexpr
from sqlalchemy import Table


class LibInfoDao:
    table: Table = LibInfo.__table__
    _ins = table.insert()
    _sel = table.select()
    _upd = table.update()
    _del = table.delete()

    @classmethod
    def _gen_and_list(cls, key: dict):
        andList = []
        for k, v in key.items():
            andList.append(getattr(cls.table.c, k) == v)
        return andList

    @classmethod
    def stmt_add(cls, x: dict):
        stmt = cls._ins.values(**x)
        return stmt

    @classmethod
    def stmt_get_all(cls):
        stmt = cls._sel
        return stmt

    @classmethod
    def stmt_get_by_name(cls, name: str):
        stmt = cls._sel.where(cls.table.c.name == name)
        return stmt

    @classmethod
    def stmt_get_by_key(cls, key: dict):
        andList = cls._gen_and_list(key)
        stmt = cls._sel.where(sqlexpr.and_(*andList))
        return stmt

    @classmethod
    def stmt_update(cls, key: dict, val: dict):
        andList = cls._gen_and_list(key)
        stmt = cls._upd.where(sqlexpr.and_(*andList)).values(*val)
        return stmt

    @classmethod
    def stmt_del_by_name(cls, name: str):
        stmt = cls._del.where(cls.table.c.name == name)
        return stmt

    def __init__(self, exec=None):
        self.exec = exec

    def add(self, x: dict):
        stmt = self.stmt_add(x)
        self.exec(stmt)

    def get_by_name(self, name: str):
        stmt = self.stmt_get_by_name(name)
        self.exec(stmt)

    def get_by_key(self, key: dict):
        stmt = self.stmt_get_by_key(key)
        self.exec(stmt)

    def update(self, key: dict, val: dict):
        stmt = self.stmt_update(key, val)
        self.exec(stmt)

    def del_by_name(self, name: str):
        stmt = self.stmt_del_by_name(name)
        self.exec(stmt)


__all__ = ['LibInfoDao']
