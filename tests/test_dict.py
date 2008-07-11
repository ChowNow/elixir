"""
    test the deep-set functionality
"""

import sqlalchemy as sa
from elixir import *

def setup():
    metadata.bind = 'sqlite:///'

    global Table1, Table2, Table3
    class Table1(Entity):
        t1id = Field(Integer, primary_key=True)
        name = Field(String(30))
        tbl2s = OneToMany('Table2')
        tbl3 = OneToOne('Table3')

    class Table2(Entity):
        t2id = Field(Integer, primary_key=True)
        name = Field(String(30))
        tbl1 = ManyToOne(Table1)

    class Table3(Entity):
        t3id = Field(Integer, primary_key=True)
        name = Field(String(30))
        tbl1 = ManyToOne(Table1)

    setup_all(True)

def teardown():
    cleanup_all(True)

class TestDeepSet(object):
    def test_set_attr(self):
        t1 = Table1()
        t1.from_dict(dict(name='test1'))
        assert t1.name == 'test1'

    def test_nonset_attr(self):
        t1 = Table1(name='test2')
        t1.from_dict({})
        assert t1.name == 'test2'

    def test_set_rel(self):
        t1 = Table1()
        t1.from_dict(dict(tbl3={'name': 'bob'}))
        assert t1.tbl3.name == 'bob'

    def test_remove_rel(self):
        t1 = Table1()
        t1.tbl3 = Table3()
        t1.from_dict(dict(tbl3=None))
        assert t1.tbl3 is None

    def test_update_rel(self):
        t1 = Table1()
        t1.tbl3 = Table3(name='fred')
        t1.from_dict(dict(tbl3={'name': 'bob'}))
        assert t1.tbl3.name == 'bob'

    def test_extend_list(self):
        t1 = Table1()
        t1.from_dict(dict(tbl2s=[{'name': 'test3'}]))
        assert len(t1.tbl2s) == 1
        assert t1.tbl2s[0].name == 'test3'

    def test_truncate_list(self):
        t1 = Table1()
        t2 = Table2()
        t1.tbl2s.append(t2)
        session.commit()
        t1.from_dict(dict(tbl2s=[]))
        assert len(t1.tbl2s) == 0

    def test_update_list_item(self):
        t1 = Table1()
        t2 = Table2()
        t1.tbl2s.append(t2)
        session.commit()
        t1.from_dict(dict(tbl2s=[{'t2id': t2.t2id, 'name': 'test4'}]))
        assert len(t1.tbl2s) == 1
        assert t1.tbl2s[0].name == 'test4'

    def test_invalid_update(self):
        t1 = Table1()
        t2 = Table2()
        t1.tbl2s.append(t2)
        session.commit()
        try:
            t1.from_dict(dict(tbl2s=[{'t2id':t2.t2id+1}]))
            assert False
        except:
            pass

    def test_to(self):
        t1 = Table1(t1id=50, name='test1')
        assert t1.to_dict() == {'t1id': 50, 'name': 'test1'}

    def test_to_deep(self):
        t1 = Table1(t1id=51, name='test2')
        assert t1.to_dict(deep={'tbl2s':{}}) == \
                {'t1id': 51, 'name': 'test2', 'tbl2s': []}

    def test_to_deep2(self):
        t1 = Table1(t1id=52, name='test3')
        t2 = Table2(t2id=50, name='test4')
        t1.tbl2s.append(t2)
        session.commit()
        assert t1.to_dict(deep={'tbl2s':{}}) == \
                {'t1id': 52,
                 'name': 'test3',
                 'tbl2s': [{'t2id': 50, 'name': 'test4'}]}

    def test_to_deep3(self):
        t1 = Table1(t1id=53, name='test2')
        t1.tbl3 = Table3(t3id=50, name='wobble')
        session.commit()
        assert t1.to_dict(deep={'tbl3':{}}) == \
                {'t1id': 53,
                 'name': 'test2',
                 'tbl3': {'t3id': 50, 'name': 'wobble'}}

class TestSetOnAliasedColumn(object):
    def setup(self):
        metadata.bind = 'sqlite:///'
        session.clear()

    def teardown(self):
        cleanup_all(True)

    def test_set_on_aliased_column(self):
        class A(Entity):
            name = Field(String(60), colname='strName')

        setup_all(True)

        a = A()
        a.set(name='Aye')

        assert a.name == 'Aye'
        session.commit()
        session.clear()

