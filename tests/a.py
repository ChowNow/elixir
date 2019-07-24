from __future__ import absolute_import

from elixir import *

class A(Entity):
    name = Field(String(30))
    b = ManyToOne('tests.b.B')
