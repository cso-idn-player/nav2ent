# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class BspFile(KaitaiStruct):
    """BSP file format that's commonly used by GoldSrc engine games.
    
    .. seealso::
       Source - https://github.com/valvesoftware/halflife/blob/master/utils/common/bspfile.c
    
    
    .. seealso::
       Source - https://github.com/valvesoftware/halflife/blob/master/utils/common/bspfile.h
    """

    class LumpType(Enum):
        entities = 0
        planes = 1
        textures = 2
        vertexes = 3
        visibility = 4
        nodes = 5
        texinfo = 6
        faces = 7
        lighting = 8
        clipnodes = 9
        leafs = 10
        marksurfaces = 11
        edges = 12
        surfedges = 13
        models = 14
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.version = self._io.read_s4le()
        if not self.version == 30:
            raise kaitaistruct.ValidationNotEqualError(30, self.version, self._io, u"/seq/0")
        self.lumps = []
        for i in range(15):
            self.lumps.append(BspFile.Lump(i, self._io, self, self._root))


    class Lump(KaitaiStruct):
        """The BSP lump.
        """
        def __init__(self, ks_params_index, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.ks_params_index = ks_params_index
            self._read()

        def _read(self):
            self.content_offset = self._io.read_s4le()
            self.content_size = self._io.read_s4le()

        @property
        def ks_instances_type(self):
            """Lump type."""
            if hasattr(self, '_m_ks_instances_type'):
                return self._m_ks_instances_type

            self._m_ks_instances_type = KaitaiStream.resolve_enum(BspFile.LumpType, self.ks_params_index)
            return getattr(self, '_m_ks_instances_type', None)

        @property
        def ks_instances_content(self):
            """Lump data."""
            if hasattr(self, '_m_ks_instances_content'):
                return self._m_ks_instances_content

            _pos = self._io.pos()
            self._io.seek(self.content_offset)
            _on = self.ks_instances_type
            if _on == BspFile.LumpType.entities:
                self._raw__m_ks_instances_content = self._io.read_bytes(self.content_size)
                _io__raw__m_ks_instances_content = KaitaiStream(BytesIO(self._raw__m_ks_instances_content))
                self._m_ks_instances_content = BspFile.LumpContentEntities(_io__raw__m_ks_instances_content, self, self._root)
            else:
                self._m_ks_instances_content = self._io.read_bytes(self.content_size)
            self._io.seek(_pos)
            return getattr(self, '_m_ks_instances_content', None)


    class LumpContentEntities(KaitaiStruct):
        """Entities lump.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.blocks = (KaitaiStream.bytes_terminate(self._io.read_bytes_full(), 0, False)).decode(u"ascii")



