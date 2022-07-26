from enum import EnumMeta, auto
from math import ceil, floor, sqrt
from sys import modules
from typing import Type
from warnings import warn
from kaitaistruct import KaitaiStream
from ._nav_cscz import *



GENERATION_STEP_SIZE: float = 25.0
"""(30) was 20, but bots can't fit always fit."""
STEP_HEIGHT: float = 18.0
"""If delta Z is greater than this, we have to jump to get up."""
HUMAN_HEIGHT_HALF: float = 36.0
GRID_CELL_SIZE: float = 300.0


class NavErrorType (Enum):
    NAV_OK = 0
    NAV_CANT_ACCESS_FILE = auto()
    NAV_INVALID_FILE = auto()
    NAV_BAD_FILE_VERSION = auto()
    NAV_CORRUPT_DATA = auto()


class NavException (Exception):
    def __init__(self, error_type: NavErrorType, error_msg: str, *args: object) -> None:
        super().__init__( (error_type, error_msg,), *args )


# Extract all classes & enums.
for k,v in NavCsczFile.__dict__.items():
    if type(v) in [type, EnumMeta]:
        setattr( modules[__name__], k, v )
# Silence, linter!
DirectionType: Type[NavCsczFile.DirectionType] = DirectionType
ApproachInfo: Type[NavCsczFile.ApproachInfo] = ApproachInfo


NUM_DIRECTIONS: int = DirectionType.num_directions.value
"""Directions count."""


def OppositeDirection (dir: DirectionType) -> DirectionType:
    if dir == DirectionType.north:
        return DirectionType.south
    elif dir == DirectionType.south:
        return DirectionType.north
    elif dir == DirectionType.east:
        return DirectionType.west
    elif dir == DirectionType.west:
        return DirectionType.east
    return DirectionType.north


class Vector (NavCsczFile.Vector):
    @classmethod
    def from_list (cls: "Vector", v: list[float], _parent=None, _root=None):
        self = cls.from_bytes( b''.join(KaitaiStream.packer_f4le.pack(x) for x in v) )
        self._parent = _parent
        self._root = _root if _root else self
        return self

    def copy (self: "Vector"):
        return Vector.from_list([
            self.x
            , self.y
            , self.z
        ])

    @property
    def keyvalue (self: "Vector"):
        """Keyvalue string of this vector."""
        return " ".join( str(int(x)) for x in self )

    @property
    def length (self: "Vector"):
        """Length of this vector."""
        return sqrt( self.x*self.x + self.y*self.y + self.z*self.z )

    def update (self: "Vector", other: "Vector"):
        (self.x
        , self.y
        , self.z) = (other.x, other.y, other.z)

    def __str__ (self: "Vector"):
        return f"{self.x} {self.y} {self.z}"

    def __bytes__ (self: "Vector"):
        return b''.join( KaitaiStream.packer_f4le.pack(x) for x in self )

    def __len__ (self: "Vector"):
        return self.length

    def __hash__ (self) -> int:
        return hash( tuple(self) )

    def __iter__ (self: "Vector"):
        return iter([ self.x, self.y, self.z ])

    def __eq__ (self, other: "Vector") -> bool:
        return tuple(self) == tuple(other)

    def __add__ (self: "Vector", other: "Vector"):
        return Vector.from_list([
            self.x + other.x
            , self.y + other.y
            , self.z + other.z
        ])

    def __sub__ (self: "Vector", other: "Vector"):
        return Vector.from_list([
            self.x - other.x
            , self.y - other.y
            , self.z - other.z
        ])

    def __mul__ (self: "Vector", v: int|float):
        return Vector.from_list([
            self.x * v
            , self.y * v
            , self.z * v
        ])

    def _vector_div (self: "Vector", v: int|float, floordiv = False):
        result = [
            self.x / v
            , self.y / v
            , self.z / v
        ]
        if floordiv:
            result = [floor(x) for x in result]
        return result

    def __truediv__ (self: "Vector", v: int|float):
        return Vector.from_list( self._vector_div(v) )

    def __floordiv__ (self: "Vector", v: int|float):
        return Vector.from_list( self._vector_div(v, True) )


NavCsczFile.Vector = Vector
VECTOR_ZERO: Vector = Vector.from_list([ 0,0,0 ])
"""Zero vector."""


class Ray (NavCsczFile.Ray):
    @classmethod
    def from_list (cls: "Ray", v: list[float], _parent=None, _root=None):
        self = cls.from_bytes( b''.join(bytes(x) for x in v) )
        self._parent = _parent
        self._root = _root if _root else self
        return self


NavCsczFile.Ray = Ray


class Extent (NavCsczFile.Extent):
    @property
    def ks_instances_delta (self) -> Vector:
        return self.hi - self.lo

    @property
    def ks_instances_size (self) -> float:
        return self.ks_instances_delta.x * self.ks_instances_delta.y

    @property
    def ks_instances_center (self) -> Vector:
        return (self.lo + self.hi) / 2.0


NavCsczFile.Extent = Extent


class Place (NavCsczFile.Place):
    def __str__ (self) -> str:
        return self.name


NavCsczFile.Place = Place


THE_HIDING_SPOT_LIST = list["HidingSpot"]()
"""List of hiding spots."""


def GetHidingSpotByID (id: int):
    """Given a HidingSpot ID, return the associated HidingSpot."""
    for spot in THE_HIDING_SPOT_LIST:
        if spot.id == id:
            return spot
    return None


class HidingSpot (NavCsczFile.HidingSpot):
    def __init__ (self, _io, _parent=None, _root=None):
        super().__init__( _io, _parent, _root )
        THE_HIDING_SPOT_LIST.append( self )


NavCsczFile.HidingSpot = HidingSpot


class NavArea (NavCsczFile.NavArea):
    def PostLoad (self: "NavArea") -> NavErrorType:
        """Convert loaded IDs to pointers.
        Make sure all IDs are converted, even if corrupt data is encountered.
        """
        error = NavErrorType.NAV_OK
        # connect areas together.
        for d in range( NUM_DIRECTIONS ):
            for connect in self.area_adjacents_per_directions[d].entries:
                connect: NavConnect= connect
                if connect.area_id and not connect.area:
                    warn(
                        f"Corrupt navigation data. Cannot connect Navigation Areas."
                        , RuntimeWarning
                    )
                    error = NavErrorType.NAV_CORRUPT_DATA

        # resolve approach area IDs.
        for a in self.approach_areas.entries:
            a: ApproachInfo = a
            aca = a.here
            if aca.area_id and not aca.area:
                warn(
                    f"Corrupt navigation data. Missing Approach Area (here)."
                    , RuntimeWarning
                )
                error = NavErrorType.NAV_CORRUPT_DATA
            aca = a.prev.area_connection
            if aca.area_id and not aca.area:
                warn(
                    f"Corrupt navigation data. Missing Approach Area (prev)."
                    , RuntimeWarning
                )
                error = NavErrorType.NAV_CORRUPT_DATA
            aca = a.next.area_connection
            if aca.area_id and not aca.area:
                warn(
                    f"Corrupt navigation data. Missing Approach Area (next)."
                    , RuntimeWarning
                )
                error = NavErrorType.NAV_CORRUPT_DATA

        # resolve spot encounter IDs.
        for e in self.encounter_spots.entries:
            e: EncounterSpot = e
            f = e.source
            t = e.target

            f_eac = f.area_connection
            if not f_eac.area:
                warn(
                    f"Corrupt navigation data. Missing \"from\" Navigation Area for Encounter Spot."
                    , RuntimeWarning
                )
                error = NavErrorType.NAV_CORRUPT_DATA

            t_eac = t.area_connection
            if not t_eac.area:
                warn(
                    f"Corrupt navigation data. Missing \"to\" Navigation Area for Encounter Spot."
                    , RuntimeWarning
                )
                error = NavErrorType.NAV_CORRUPT_DATA

            if f_eac.area and t_eac.area:
                # compute path.
                e.path.target, _ = self.ComputePortal( t_eac.area, t.direction )
                e.path.source, _ = self.ComputePortal( f_eac.area, f.direction )
                eyeHeight = HUMAN_HEIGHT_HALF
                e.path.source.z = f_eac.area.GetZ( e.path.source ) + eyeHeight
                e.path.target.z = t_eac.area.GetZ( e.path.target ) + eyeHeight

            # resolve HidingSpot IDs.
            for order in e.spots:
                if not order.hiding_spot:
                    warn(
                        f"Corrupt navigation data. Missing Hiding Spot."
                        , RuntimeWarning
                    )
                    error = NavErrorType.NAV_CORRUPT_DATA

        # build overlap list.
        ## TODO: Optimize this.
        '''for( NavAreaList::iterator oiter = TheNavAreaList.begin(); oiter != TheNavAreaList.end(); ++oiter )
        {
            CNavArea *area = *oiter;

            if (area == this)
                continue;

            if (IsOverlapping( area ))
                m_overlapList.push_back( area );
        }'''
        return error

    def IsOverlapping (self: "NavArea", pos: Vector) -> bool:
        """Return true if 'pos' is within 2D extents of area."""
        return(
            pos.x >= self.area_extent.lo.x
            and pos.x <= self.area_extent.hi.x
            and pos.y >= self.area_extent.lo.y
            and pos.y <= self.area_extent.hi.y
        )

    def GetZ (self: "NavArea", pos: Vector) -> float:
        """Return Z of area at (x,y) of 'pos'
        Trilinear interpolation of Z values at quad edges.
        NOTE: pos->z is not used.
        """
        m_neZ = self.corner_northeast_z
        m_swZ = self.corner_southwest_z
        m_extent = self.area_extent
        dx: float = m_extent.hi.x - m_extent.lo.x
        dy: float = m_extent.hi.y - m_extent.lo.y
        # guard against division by zero due to degenerate areas.
        if dx == 0.0 or dy == 0.0:
            return m_neZ

        u: float = (pos.x - m_extent.lo.x) / dx
        v: float = (pos.y - m_extent.lo.y) / dy
        # clamp Z values to (x,y) volume.
        if u < 0.0:
            u = 0.0
        elif u > 1.0:
            u = 1.0
        if v < 0.0:
            v = 0.0
        elif v > 1.0:
            v = 1.0

        northZ: float = m_extent.lo.z + u * (m_neZ - m_extent.lo.z)
        southZ: float = m_swZ + u * (m_extent.hi.z - m_swZ)
        return northZ + v * (southZ - northZ)

    def GetClosestPointOnArea (self: "NavArea", pos: Vector) -> Vector:
        """Return closest point to 'pos' on 'area'."""
        extent = self.area_extent
        close: Vector = VECTOR_ZERO.copy()
        if pos.x < extent.lo.x:
            if pos.y < extent.lo.y:
                # position is north-west of area.
                close = extent.lo.copy()
            elif pos.y > extent.hi.y:
                # position is south-west of area
                close.x = extent.lo.x
                close.y = extent.hi.y
            else:
                # position is west of area.
                close.x = extent.lo.x
                close.y = pos.y
        elif pos.x > extent.hi.x:
            if pos.y < extent.lo.y:
                # position is north-east of area
                close.x = extent.hi.x
                close.y = extent.lo.y
            elif pos.y > extent.hi.y:
                # position is south-east of area
                close = extent.hi.copy()
            else:
                # position is east of area
                close.x = extent.hi.x
                close.y = pos.y
        elif pos.y < extent.lo.y:
            # position is north of area
            close.x = pos.x
            close.y = extent.lo.y
        elif pos.y > extent.hi.y:
            # position is south of area
            close.x = pos.x
            close.y = extent.hi.y
        else:
            # position is inside of area - it is the 'closest point' to itself
            close = pos.copy()
        close.z = self.GetZ( close )
        return close

    def IsDegenerate (self: "NavArea") -> bool:
        """Return true if this area is badly formed."""
        ext = self.area_extent
        return ext.lo.x >= ext.hi.x or ext.lo.y >= ext.hi.y

    def ComputePortal (self: "NavArea", target: "NavArea", dir: DirectionType):
        """Compute "portal" between to adjacent areas.
        Return center of portal opening, and half-width defining sides of portal from center.
        NOTE: center->z is unset.
        """
        center: Vector = VECTOR_ZERO.copy()
        halfWidth: float = 0.0
        src_ext = self.area_extent
        tgt_ext = target.area_extent
        if dir == DirectionType.north or dir == DirectionType.south:
            if dir == DirectionType.north:
                center.y = src_ext.lo.y
            else:
                center.y = src_ext.hi.y

            left: float = max( src_ext.lo.x, tgt_ext.lo.x )
            right: float = min( src_ext.hi.x, tgt_ext.hi.x )
            # clamp to our extent in case areas are disjoint.
            if left < src_ext.lo.x:
                left = src_ext.lo.x
            elif left > src_ext.hi.x:
                left = src_ext.hi.x
            if right < src_ext.lo.x:
                right = src_ext.lo.x
            elif right > src_ext.hi.x:
                right = src_ext.hi.x
            center.x = (left + right) / 2.0
            halfWidth = (right - left) / 2.0
        else:
            # EAST or WEST.
            if dir == DirectionType.west:
                center.x = src_ext.lo.x
            else:
                center.x = src_ext.hi.x

            top: float = max( src_ext.lo.y, tgt_ext.lo.y )
            bottom: float = min( src_ext.hi.y, tgt_ext.hi.y )
            # clamp to our extent in case areas are disjoint.
            if top < src_ext.lo.y:
                top = src_ext.lo.y
            elif top > src_ext.hi.y:
                top = src_ext.hi.y
            if bottom < src_ext.lo.y:
                bottom = src_ext.lo.y
            elif bottom > src_ext.hi.y:
                bottom = src_ext.hi.y
            center.y = (top + bottom) / 2.0
            halfWidth = (bottom - top) / 2.0
        return (center, halfWidth)

    def get_aligned_origin (self: "NavArea", pos: Vector) -> Vector|None:
        if not self.IsOverlapping( pos ):
            return None
        result: Vector = pos.copy()
        result.z = self.GetZ( pos )
        return result

    def __hash__ (self) -> int:
        return hash( self.id )

    def __eq__ (self: "NavArea", other: "NavArea"):
        return other and self.id == other.id

    def __lt__ (self: "NavArea", other: "NavArea"):
        return other and self.id < other.id

    def __le__ (self: "NavArea", other: "NavArea"):
        return other and self.id <= other.id


NavCsczFile.NavArea = NavArea


class EncounterSpot (NavCsczFile.EncounterSpot):
    def __init__ (self, _io, _parent=None, _root=None):
        super().__init__( _io, _parent, _root )
        self.path = Ray.from_list([ VECTOR_ZERO, VECTOR_ZERO ])


NavCsczFile.EncounterSpot = EncounterSpot


class EncounterSpotOrder (NavCsczFile.EncounterSpotOrder):
    @property
    def hiding_spot (self: "EncounterSpotOrder"):
        """HidingSpot object of this connection."""
        return GetHidingSpotByID( self.hiding_spot_id )


NavCsczFile.EncounterSpotOrder = EncounterSpotOrder


class NavConnect (NavCsczFile.NavConnect):
    @property
    def area (self: "NavConnect"):
        """NavArea object of this connection."""
        return THE_NAV_AREA_GRID.GetNavAreaByID( self.area_id )

    def __str__ (self: "NavConnect") -> str:
        return str( self.area_id )


NavCsczFile.NavConnect = NavConnect


class NavAreaGridHash ():
    """Hash link of a grid NavArea.
    """
    def __init__ (self, area: NavArea) -> None:
        self.m_hereArea = area
        self.m_prevHash: "NavAreaGridHash"|None = None
        self.m_nextHash: "NavAreaGridHash"|None = None

    def __eq__ (self, other: "NavAreaGridHash") -> bool:
        return self.m_hereArea == other.m_hereArea


class NavAreaGrid ():
    """The CNavAreaGrid is used to efficiently access navigation areas by world position.
    Each cell of the grid contains a list of areas that overlap it.
    Given a world position, the corresponding grid cell is ( x/cellsize, y/cellsize ).
    """
    @staticmethod
    def ComputeHashKey (id: int) -> int:
        """Returns a hash key for the given nav area ID."""
        return id & 0xFF

    def __init__(self) -> None:
        self.m_grid: list[list[NavAreaGridHash]] = []
        self.m_minX: float = 0.0
        self.m_minY: float = 0.0
        self.m_hashTable: list[NavAreaGridHash|None] = [None,] * 256
        """Hash table to optimize lookup by ID."""
        self.Reset()

    def Reset (self):
        """Clear the grid."""
        self.m_grid.clear()
        self.m_gridSizeX: int = 0
        self.m_gridSizeY: int = 0
        # clear the hash table.
        for k in range(len(self.m_hashTable)):
            self.m_hashTable[k] = None
        self._areaCount: int = 0
        """Total number of nav areas."""

    def Initialize (self, minX: float, maxX: float, minY: float, maxY: float):
        """Clear and reset the grid to the given extents."""
        if self.m_grid:
            self.Reset()
        # Allocate the grid and define its extents.
        self.m_minX = minX
        self.m_minY = minY
        sx = self.m_gridSizeX = int((maxX - minX) / GRID_CELL_SIZE) + 1
        sy = self.m_gridSizeY = int((maxY - minY) / GRID_CELL_SIZE) + 1
        size: int = ceil( sx * sy )
        self.m_grid.extend( [] for _ in range(size) )
        assert( len(self.m_grid) == size )

    def AddNavArea (self, area: NavArea):
        """Add an area to the grid."""
        # add to grid.
        extent = area.area_extent
        loX = self.WorldToGridX( extent.lo.x )
        loY = self.WorldToGridY( extent.lo.y )
        hiX = self.WorldToGridX( extent.hi.x )
        hiY = self.WorldToGridY( extent.hi.y )

        here_hash = NavAreaGridHash( area )
        for y in range(loY, hiY+1):
            for x in range(loX, hiX+1):
                self.m_grid[ x + y*self.m_gridSizeX ].append( here_hash )

        # add to hash table.
        key: int = self.ComputeHashKey( area.id )
        if self.m_hashTable[key]:
            # add to head of list in this slot.
            here_hash.m_prevHash = None
            here_hash.m_nextHash = self.m_hashTable[key]
            self.m_hashTable[key].m_prevHash = here_hash
            self.m_hashTable[key] = here_hash
        else:
            # first entry in this slot.
            self.m_hashTable[key] = here_hash
            here_hash.m_nextHash = None
            here_hash.m_prevHash = None
        self._areaCount += 1
        assert( self._areaCount >= 0 )
        return here_hash

    def RemoveNavArea (self, area_hash: NavAreaGridHash|NavArea):
        if isinstance( area_hash, NavArea ):
            area_hash = self.get_hash_area_by_id( area_hash.id )
            if not area_hash:
                return
        """Remove an area from the grid."""
        area = area_hash.m_hereArea
        extent = area.area_extent
        loX = self.WorldToGridX( extent.lo.x )
        loY = self.WorldToGridY( extent.lo.y )
        hiX = self.WorldToGridX( extent.hi.x )
        hiY = self.WorldToGridY( extent.hi.y )

        for y in range(loY, hiY+1):
            for x in range(loX, hiX+1):
                self.m_grid[ x + y*self.m_gridSizeX ].remove( area_hash )

        # remove from hash table.
        key: int = self.ComputeHashKey( area.id )
        if area_hash.m_prevHash:
            area_hash.m_prevHash.m_nextHash = area_hash.m_nextHash
        else:
            # area was at start of list.
            self.m_hashTable[key] = area_hash.m_nextHash
            if self.m_hashTable[key]:
                self.m_hashTable[key].m_prevHash = None
        if area_hash.m_nextHash:
            area_hash.m_nextHash.m_prevHash = area_hash.m_prevHash
        self._areaCount -= 1
        assert( self._areaCount >= 0 )

    def GetNavAreaCount (self) -> int:
        """Return total number of nav areas."""
        return self._areaCount

    def GetNavArea (self, pos: Vector, beneathLimit: float = 120.0 ) -> NavArea | None:
        """Given a position, return the nav area that IsOverlapping and is *immediately* beneath it."""
        if not self.m_grid:
            return None

        # get list in cell that contains position.
        x: int = self.WorldToGridX( pos.x )
        y: int = self.WorldToGridY( pos.y )
        area_list: list[NavAreaGridHash] = self.m_grid[ x + y*self.m_gridSizeX ]

        # search cell list to find correct area.
        use: NavAreaGridHash = None
        useZ: float = -99999999.9
        testPos: Vector = pos + Vector.from_list([0, 0, 5])
        for area_hash in area_list:
            area: NavArea = area_hash.m_hereArea
            # check if position is within 2D boundaries of this area.
            if area.IsOverlapping( testPos ):
                # project position onto area to get Z.
                z: float = area.GetZ( testPos )

                # if area is above us, skip it.
                if z > testPos.z:
                    continue

                # if area is too far below us, skip it.
                if z < pos.z - beneathLimit:
                    continue

                # if area is higher than the one we have, use this instead.
                if z > useZ:
                    use = area
                    useZ = z
        return use

    def GetNavAreaByID (self, id: int) -> NavArea | None:
        """Given an ID, return the associated area."""
        area_hash = self.get_hash_area_by_id( id )
        if area_hash:
            return area_hash.m_hereArea
        return None

    def GetNearestNavArea (self, pos: Vector, anyZ: bool = False) -> NavArea | None:
        """Given a position in the world, return the nav area that is closest
        and at the same height, or beneath it.
        Used to find initial area if we start off of the mesh.
        """
        raise NotImplementedError( "GetNearestNavArea" )

    def GetPlace (self, pos: Vector) -> int:
        """Return radio chatter place for given coordinate."""
        raise NotImplementedError( "GetPlace" )

    def WorldToGridX (self, wx: float) -> int:
        x: int = int( (wx - self.m_minX) / GRID_CELL_SIZE )
        if x < 0:
            x = 0
        elif x >= self.m_gridSizeX:
            x = self.m_gridSizeX - 1
        return x

    def WorldToGridY (self, wy: float) -> int:
        y: int = int( (wy - self.m_minY) / GRID_CELL_SIZE )
        if y < 0:
            y = 0
        elif y >= self.m_gridSizeY:
            y = self.m_gridSizeY - 1
        return y

    def get_hash_area_by_id (self, id: int) -> NavAreaGridHash | None:
        """Given an ID, return the associated hash area."""
        if id == 0:
            return None

        key: int = self.ComputeHashKey( id )
        area_hash = self.m_hashTable[key]
        while area_hash:
            if area_hash.m_hereArea.id == id:
                return area_hash
            area_hash = area_hash.m_nextHash
        return None

    def load (self, areas: list[NavArea]) -> NavErrorType:
        lo = Vector.from_list([ 9999999999.9, 9999999999.9, 0 ])
        hi = Vector.from_list([ -9999999999.9, -9999999999.9, 0 ])
        # load the areas and compute total extent.
        for area in areas:
            areaExtent = area.area_extent
            # check validity of nav area.
            if areaExtent.lo.x >= areaExtent.hi.x or areaExtent.lo.y >= areaExtent.hi.y:
                warn(
                    f"Degenerate Navigation Area #{area.id} at ( {str(areaExtent.ks_instances_center)} )"
                    , RuntimeWarning
                )
            if (areaExtent.lo.x < lo.x):
                lo.x = areaExtent.lo.x
            if (areaExtent.lo.y < lo.y):
                lo.y = areaExtent.lo.y
            if (areaExtent.hi.x > hi.x):
                hi.x = areaExtent.hi.x
            if (areaExtent.hi.y > hi.y):
                hi.y = areaExtent.hi.y
        # add the areas to the grid
        self.Initialize( lo.x, hi.x, lo.y, hi.y )
        for area in areas:
            self.AddNavArea( area )
        return NavErrorType.NAV_OK


THE_NAV_AREA_GRID = NavAreaGrid()
"""The singleton for accessing the grid."""
