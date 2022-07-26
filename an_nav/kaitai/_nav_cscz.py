# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class NavCsczFile(KaitaiStruct):
    """A Kaitai struct for CS 1.6/CSCZ bot AI navigation (.NAV) files.
    
    .. seealso::
       Source - https://github.com/ValveSoftware/halflife/tree/master/game_shared/bot
    """

    class DirectionType(Enum):
        north = 0
        east = 1
        south = 2
        west = 3
        num_directions = 4

    class TransverseType(Enum):
        go_north = 0
        go_east = 1
        go_south = 2
        go_west = 3
        go_ladder_up = 4
        go_ladder_down = 5
        go_jump = 6
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic_number = self._io.read_u4le()
        if not self.magic_number == 4277009102:
            raise kaitaistruct.ValidationNotEqualError(4277009102, self.magic_number, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        _ = self.version
        if not _ <= 5:
            raise kaitaistruct.ValidationExprError(self.version, self._io, u"/seq/1")
        if self.version >= 4:
            self.bsp_size = self._io.read_u4le()

        if self.ks_instances_can_has_places:
            self.places = NavCsczFile.PlaceList(self._io, self, self._root)

        self.nav_areas = NavCsczFile.NavAreaList(self._io, self, self._root)

    class PlaceList(KaitaiStruct):
        """The 'place directory' is used to save and load places from
        nav files in a size-efficient manner that also allows for the
        order of the place ID's to change without invalidating the
        nav files.
        
        The place directory is stored in the nav file as a list of
        place name strings.  Each nav area then contains an index
        into that directory, or zero if no place has been assigned to
        that area.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u2le()
            self.entries = []
            for i in range(self.count):
                self.entries.append(NavCsczFile.Place(self._io, self, self._root))



    class NavAreaList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u4le()
            self.entries = []
            for i in range(self.count):
                self.entries.append(NavCsczFile.NavArea(self._io, self, self._root))



    class EncounterSpotList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u4le()
            self.entries = []
            for i in range(self.count):
                _on = self.ks_instances_is_legacy
                if _on == True:
                    self.entries.append(NavCsczFile.EncounterSpotLegacy(self._io, self, self._root))
                elif _on == False:
                    self.entries.append(NavCsczFile.EncounterSpot(self._io, self, self._root))


        @property
        def ks_instances_is_legacy(self):
            """Return true if encounter spots are legacy version."""
            if hasattr(self, '_m_ks_instances_is_legacy'):
                return self._m_ks_instances_is_legacy

            self._m_ks_instances_is_legacy = self._root.version < 3
            return getattr(self, '_m_ks_instances_is_legacy', None)


    class Extent(KaitaiStruct):
        """Extents of area in world coords.
        NOTE: lo.z is not necessarily the minimum Z, but corresponds to Z at point (lo.x, lo.y), etc.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lo = NavCsczFile.Vector(self._io, self, self._root)
            self.hi = NavCsczFile.Vector(self._io, self, self._root)

        @property
        def ks_instances_delta(self):
            """hi - lo."""
            if hasattr(self, '_m_ks_instances_delta'):
                return self._m_ks_instances_delta

            self._m_ks_instances_delta = [(self.hi.x - self.lo.x), (self.hi.y - self.lo.y), (self.hi.z - self.lo.z)]
            return getattr(self, '_m_ks_instances_delta', None)

        @property
        def ks_instances_size(self):
            """delta X * delta Y."""
            if hasattr(self, '_m_ks_instances_size'):
                return self._m_ks_instances_size

            self._m_ks_instances_size = (self.ks_instances_delta[0] * self.ks_instances_delta[1])
            return getattr(self, '_m_ks_instances_size', None)

        @property
        def ks_instances_center(self):
            """Centroid of area."""
            if hasattr(self, '_m_ks_instances_center'):
                return self._m_ks_instances_center

            self._m_ks_instances_center = [((self.lo.x + self.hi.x) / 2.0), ((self.lo.y + self.hi.y) / 2.0), ((self.lo.z + self.hi.z) / 2.0)]
            return getattr(self, '_m_ks_instances_center', None)


    class HidingSpotList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u1()
            self.entries = []
            for i in range(self.count):
                _on = self.ks_instances_is_legacy
                if _on == True:
                    self.entries.append(NavCsczFile.Vector(self._io, self, self._root))
                elif _on == False:
                    self.entries.append(NavCsczFile.HidingSpot(self._io, self, self._root))


        @property
        def ks_instances_is_legacy(self):
            """Return true if hiding spots are vectors list."""
            if hasattr(self, '_m_ks_instances_is_legacy'):
                return self._m_ks_instances_is_legacy

            self._m_ks_instances_is_legacy = self._root.version == 1
            return getattr(self, '_m_ks_instances_is_legacy', None)


    class HidingSpotFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.in_cover = self._io.read_bits_int_le(1) != 0
            self.good_sniper_shot = self._io.read_bits_int_le(1) != 0
            self.ideal_sniper_shot = self._io.read_bits_int_le(1) != 0


    class ApproachInfoConnect(KaitaiStruct):
        def __init__(self, ks_params_is_previous, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.ks_params_is_previous = ks_params_is_previous
            self._read()

        def _read(self):
            self.area_connection = NavCsczFile.NavConnect(self._io, self, self._root)
            if self.ks_params_is_previous:
                self.transverse_prev_to_here = KaitaiStream.resolve_enum(NavCsczFile.TransverseType, self._io.read_u1())

            if not (self.ks_params_is_previous):
                self.transverse_here_to_next = KaitaiStream.resolve_enum(NavCsczFile.TransverseType, self._io.read_u1())



    class Vector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


    class EncounterSpotArea(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.area_connection = NavCsczFile.NavConnect(self._io, self, self._root)
            self.direction = KaitaiStream.resolve_enum(NavCsczFile.DirectionType, self._io.read_u1())


    class EncounterSpotLegacyPoint(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown1 = NavCsczFile.Vector(self._io, self, self._root)
            self.unknown2 = self._io.read_f4le()


    class NavArea(KaitaiStruct):
        """A CNavArea is a rectangular region defining a walkable area in the map.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id = self._io.read_u4le()
            self._raw_attribute_flags = self._io.read_bytes(1)
            _io__raw_attribute_flags = KaitaiStream(BytesIO(self._raw_attribute_flags))
            self.attribute_flags = NavCsczFile.NavAreaAttributeFlags(_io__raw_attribute_flags, self, self._root)
            self.area_extent = NavCsczFile.Extent(self._io, self, self._root)
            self.corner_northeast_z = self._io.read_f4le()
            self.corner_southwest_z = self._io.read_f4le()
            self.area_adjacents_per_directions = []
            for i in range(4):
                self.area_adjacents_per_directions.append(NavCsczFile.NavConnectList(i, self._io, self, self._root))

            self.hiding_spots = NavCsczFile.HidingSpotList(self._io, self, self._root)
            self.approach_areas = NavCsczFile.ApproachInfoList(self._io, self, self._root)
            self.encounter_spots = NavCsczFile.EncounterSpotList(self._io, self, self._root)
            if self._root.ks_instances_can_has_places:
                self.place_id = self._io.read_u2le()


        @property
        def ks_instances_is_undefined_place(self):
            """ie: "no place"."""
            if hasattr(self, '_m_ks_instances_is_undefined_place'):
                return self._m_ks_instances_is_undefined_place

            self._m_ks_instances_is_undefined_place = self.place_id == 0
            return getattr(self, '_m_ks_instances_is_undefined_place', None)

        @property
        def ks_instances_place(self):
            """The Place object for this area."""
            if hasattr(self, '_m_ks_instances_place'):
                return self._m_ks_instances_place

            if not ( ((self.ks_instances_is_undefined_place)) ):
                self._m_ks_instances_place = self._parent._parent.places.entries[(self.place_id - 1)]

            return getattr(self, '_m_ks_instances_place', None)

        @property
        def ks_instances_corner_northeast(self):
            if hasattr(self, '_m_ks_instances_corner_northeast'):
                return self._m_ks_instances_corner_northeast

            self._m_ks_instances_corner_northeast = [self.area_extent.hi.x, self.area_extent.lo.y, self.corner_northeast_z]
            return getattr(self, '_m_ks_instances_corner_northeast', None)

        @property
        def ks_instances_corner_southwest(self):
            if hasattr(self, '_m_ks_instances_corner_southwest'):
                return self._m_ks_instances_corner_southwest

            self._m_ks_instances_corner_southwest = [self.area_extent.lo.x, self.area_extent.hi.y, self.corner_southwest_z]
            return getattr(self, '_m_ks_instances_corner_southwest', None)


    class NavConnectList(KaitaiStruct):
        def __init__(self, ks_params_index, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.ks_params_index = ks_params_index
            self._read()

        def _read(self):
            self.count = self._io.read_u4le()
            self.entries = []
            for i in range(self.count):
                self.entries.append(NavCsczFile.NavConnect(self._io, self, self._root))


        @property
        def ks_instances_direction(self):
            """Direction of these connections."""
            if hasattr(self, '_m_ks_instances_direction'):
                return self._m_ks_instances_direction

            self._m_ks_instances_direction = KaitaiStream.resolve_enum(NavCsczFile.DirectionType, self.ks_params_index)
            return getattr(self, '_m_ks_instances_direction', None)


    class HidingSpot(KaitaiStruct):
        """A HidingSpot is a good place for a bot to crouch and wait for enemies.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id = self._io.read_u4le()
            self.origin = NavCsczFile.Vector(self._io, self, self._root)
            self._raw_flags = self._io.read_bytes(1)
            _io__raw_flags = KaitaiStream(BytesIO(self._raw_flags))
            self.flags = NavCsczFile.HidingSpotFlags(_io__raw_flags, self, self._root)


    class ApproachInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.here = NavCsczFile.NavConnect(self._io, self, self._root)
            self.prev = NavCsczFile.ApproachInfoConnect(True, self._io, self, self._root)
            self.next = NavCsczFile.ApproachInfoConnect(False, self._io, self, self._root)


    class NavAreaAttributeFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.crouch = self._io.read_bits_int_le(1) != 0
            self.jump = self._io.read_bits_int_le(1) != 0
            self.precise = self._io.read_bits_int_le(1) != 0
            self.no_jump = self._io.read_bits_int_le(1) != 0


    class EncounterSpotOrder(KaitaiStruct):
        """Stores a pointer to an interesting "spot", and a parametric distance along a path.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hiding_spot_id = self._io.read_u4le()
            self.t_char = self._io.read_u1()

        @property
        def ks_instances_t(self):
            """Parametric distance along ray where this spot first has LOS to our path.
            """
            if hasattr(self, '_m_ks_instances_t'):
                return self._m_ks_instances_t

            self._m_ks_instances_t = (self.t_char / 255.0)
            return getattr(self, '_m_ks_instances_t', None)


    class Ray(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.source = NavCsczFile.Vector(self._io, self, self._root)
            self.target = NavCsczFile.Vector(self._io, self, self._root)


    class NavConnect(KaitaiStruct):
        """The NavConnect union is used to refer to connections to areas."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.area_id = self._io.read_u4le()


    class ApproachInfoList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u1()
            self.entries = []
            for i in range(self.count):
                self.entries.append(NavCsczFile.ApproachInfo(self._io, self, self._root))



    class EncounterSpot(KaitaiStruct):
        """This struct stores possible path segments thru a CNavArea, and the dangerous spots
        to look at as we traverse that path segment.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.source = NavCsczFile.EncounterSpotArea(self._io, self, self._root)
            self.target = NavCsczFile.EncounterSpotArea(self._io, self, self._root)
            self.spots_count = self._io.read_u1()
            self.spots = []
            for i in range(self.spots_count):
                self.spots.append(NavCsczFile.EncounterSpotOrder(self._io, self, self._root))



    class Place(KaitaiStruct):
        """A place is a named group of navigation areas."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name_length = self._io.read_u2le()
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(self.name_length), 0, False)).decode(u"ascii")


    class EncounterSpotLegacy(KaitaiStruct):
        """Old data, read and discard.
        No know sample files so far.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.source = NavCsczFile.NavConnect(self._io, self, self._root)
            self.target = NavCsczFile.NavConnect(self._io, self, self._root)
            self.path = NavCsczFile.Ray(self._io, self, self._root)
            self.spots_count = self._io.read_u1()
            self.spots = []
            for i in range(self.spots_count):
                self.spots.append(NavCsczFile.EncounterSpotLegacyPoint(self._io, self, self._root))



    @property
    def ks_instances_can_has_places(self):
        """Return true if NAV file does support Place info."""
        if hasattr(self, '_m_ks_instances_can_has_places'):
            return self._m_ks_instances_can_has_places

        self._m_ks_instances_can_has_places = self.version >= 5
        return getattr(self, '_m_ks_instances_can_has_places', None)


