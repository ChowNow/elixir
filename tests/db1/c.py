from __future__ import absolute_import

from elixir import Entity, ManyToMany

class C(Entity):
    cs = ManyToMany('.b.B')
    as_ = ManyToMany('..db2.a.A')
