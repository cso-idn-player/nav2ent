from enum import EnumMeta
from sys import modules
from ..lark.ent import TRANSFORM_TYPE, EntLark
from ._bsp_basic import *



# Extract all classes & enums.
for k,v in BspFile.__dict__.items():
    if type(v) in [type, EnumMeta]:
        setattr( modules[__name__], k, v )


class LumpContentEntities (BspFile.LumpContentEntities):
    def __init__ (self, _io, _parent=None, _root=None):
        super().__init__( _io, _parent, _root )
        self.blocks: TRANSFORM_TYPE = EntLark.parse( self.blocks )


BspFile.LumpContentEntities = LumpContentEntities
