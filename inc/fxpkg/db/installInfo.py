# -*- coding:utf-8 -*-
import sqlalchemy as sa
from sqlalchemy import Table, Column, Index, Integer, BLOB, Text
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint

from .util import SaDb


class InstallEntryTable:
    key_fields = ['name', 'version', 'platform', 'arch', 'build_type']
    val_fields = [
        'include_path', 'lib_path', 'bin_path', 'cmake_path',
        'dependent','dependency',
        'other'
    ]
    
    fields = key_fields + val_fields
    real_fields = ['id'] + fields

    def __init__(self, repo):
        self.repo = repo
        self.satb = Table(
            'InstallEntry_tb', repo.metadata,
            Column('id', Integer, primary_key = True),

            Column('name', Text, index = True),
            Column('version', Text),
            Column('platform', Text),
            Column('arch', Text),
            Column('build_type', Text),

            Column('include_path', Text),
            Column('lib_path', Text),
            Column('bin_path', Text),
            Column('cmake_path', Text),

            Column('dependent', BLOB),
            Column('dependency', BLOB),

            Column('other', BLOB, server_default = ""),
            UniqueConstraint(*self.key_fields)
        )
        
    def find_entries(self, keys):
        pass

    def get_entry_by_id(self, id):
        pass


class InstallInfoRespository:
    def __init__(self, path = ':memory:'):
        url = 'sqlite:///' + str(path)
        self.db = SaDb(url)
        self.metadata = self.db.metadata
        self.InstallEntry_tb = InstallEntryTable(self)
        self.create_tables()

    def create_tables(self):
        self.db.metadata.create_all()

    def commit(self):
        return self.db.commit()
