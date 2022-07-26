from dataclasses import dataclass, field
from typing import Type
from .kaitai.nav import (
    NavCsczFile
    , NavArea
    , NavConnect
    , EncounterSpot
    , Vector
    , Ray
    , DirectionType
    , VECTOR_ZERO
    , NUM_DIRECTIONS
    , STEP_HEIGHT
    , HUMAN_HEIGHT_HALF
    , THE_NAV_AREA_GRID
    , OppositeDirection
)
from .kaitai.bsp import (
    BspFile
    , LumpContentEntities
)



AREA_INSIDE_SIZE = 200
ENTITY_OFFSET_Z_ADD = 4
ENTITY_HULL_DEFAULT_MIN: Vector = Vector.from_list([-16, -16,  0])
ENTITY_HULL_DEFAULT_MAX: Vector = Vector.from_list([ 16,  16, HUMAN_HEIGHT_HALF])


@dataclass( frozen=True, slots=True )
class InfoNodeEntity ():
    """info_node entity."""
    source: NavArea
    origin: Vector
    target: NavArea = None
    mins: Vector = field( default_factory=lambda:ENTITY_HULL_DEFAULT_MIN.copy() )
    maxs: Vector = field( default_factory=lambda:ENTITY_HULL_DEFAULT_MAX.copy() )
    absmin: Vector = field( init=False )
    absmax: Vector = field( init=False )
    merged_nodes: set["InfoNodeEntity"] = field( default_factory=set )

    def __post_init__ (self):
        absmin = self.origin.copy()
        absmin = absmin + self.mins
        object.__setattr__( self, 'absmin', absmin )
        absmax = self.origin.copy()
        absmax = absmax + self.maxs
        object.__setattr__( self, 'absmax', absmax )

    def get_id (self) -> str:
        if self.is_merged():
            return ";".join( set(str(x.source.id) for x in self.merged_nodes) )
        return str( self.source.id )

    def get_name (self) -> str:
        result = ""
        if self.is_merged():
            result = "merged"
        else:
            result = str( self.source.id )
            if self.target:
                result += f"_{self.target.id}"
        return result

    def get_place (self) -> str:
        if self.is_merged():
            return "__MERGED"
        return (
            str(self.source.ks_instances_place)
            if self.source.ks_instances_place
            else "__UNDEFINED"
    )

    def is_valid (self):
        """Check validity of this node."""
        if self.is_merged():
            return (not any(x.is_merged() for x in self.merged_nodes))
        return (self.source)

    def is_merged (self):
        return bool(self.merged_nodes)

    def get_direction (self):
        if self.is_merged():
            return None
        if self.target:
            for dir, conns in enumerate(self.source.area_adjacents_per_directions):
                for con in conns.entries:
                    if con.area == self.target:
                        return DirectionType( dir )
        return None

    def is_intersects (self, other: "InfoNodeEntity"):
        if (other.absmin.x > self.absmax.x or
            other.absmin.y > self.absmax.y or
            other.absmin.z > self.absmax.z or
            other.absmax.x < self.absmin.x or
            other.absmax.y < self.absmin.y or
            other.absmax.z < self.absmin.z
        ):
            return False
        return True

    def is_inside_of_me (self, origin: Vector):
        return (
            origin.x <= self.absmax.x and
            origin.y <= self.absmax.y and
            origin.z <= self.absmax.z and
            origin.x >= self.absmin.x and
            origin.y >= self.absmin.y and
            origin.z >= self.absmin.z
        )

    def merge (self, other: "InfoNodeEntity"):
        """Merge other node into this node.

        Return `self` in one of following conditions:
          - `other` is already in `merged_nodes`,
          - `self` is a merged node,
          - `other` is also a merged node and absorbed.

        Otherwise, return a new instance.
        """
        if other in self.merged_nodes:
            return self
        merged_list = set([ self ])
        origin = self.origin #self._merge_origin( other.origin )
        if self.is_merged():
            #self.origin.update( origin )
            if other.is_merged():
                self.merged_nodes.update( other.merged_nodes )
            else:
                self.merged_nodes.add( other )
            return self
        elif other.is_merged():
            merged_list.update( other.merged_nodes )
        else:
            merged_list.add( other )
        # Create a new merged node and return it.
        cls: Type["InfoNodeEntity"] = type( self )
        self = cls( None, origin, merged_nodes=merged_list )
        return self

    def _merge_origin (self, origin: Vector):
        return (self.origin + origin) / 2.0

    def __str__ (self) -> str:
        dir_str = self.get_direction()
        dir_str = str(dir_str.value) if dir_str else ""
        return '{\n' \
            f'"origin" "{self.origin.keyvalue}"\n' \
            f'"netname" "nav2ent_{self.get_name()}"\n' \
            f'"message" "{self.get_place()}"\n' \
            f'"sequence" "{dir_str}"\n' \
            f'"noise" "{";".join(set(x.get_name() for x in self.merged_nodes))}"\n' \
            '"classname" "info_node"\n' \
            '}\n'

    def __hash__ (self) -> int:
        return hash( self.origin )

    def __eq__ (self, other: "InfoNodeEntity") -> bool:
        return other and self.origin == other.origin


NODE_LIST = dict[InfoNodeEntity, None]()
def add_node (ent: InfoNodeEntity):
    if not ent:
        raise ValueError( "Node is None" )
    conflict = check_node_intersects( ent )
    if conflict:
        merged = conflict.merge( ent )
        if conflict.is_merged() and ent.is_merged():
            '''Assimilating a merged node.'''
            #print( f"Eat({(conflict.get_id(), ent.get_id())})", end=" " )
        elif conflict is not merged:
            '''Creating a new merged node.'''
            #print( f"New({(conflict.get_id(), ent.get_id())})", end=" " )
            #print( f"DeleteC({conflict.get_id()})", end=" " )
            NODE_LIST.pop( conflict, None )
        else:
            '''Adding a single node.'''
            #print( f"Combine({(conflict.get_id(), ent.get_id())})", end=" " )
        # Recursively to check intersects.
        return add_node( merged )
    #print( "OK" )
    NODE_LIST[ent] = None
    return ent
def check_node_intersects (ent: InfoNodeEntity):
    for node in NODE_LIST:
        if node is ent:
            continue
        if node.is_intersects(ent):
            return node
    return None
def check_node_contains (origin: Vector):
    for node in NODE_LIST:
        if node.is_inside_of_me(origin):
            return node
    return None


CONNECT_LIST = dict[NavArea, list[set[NavArea]]]()
def connect_init (area: NavArea):
    if area in CONNECT_LIST:
        return CONNECT_LIST[area]
    result = CONNECT_LIST[area] = [set[NavArea]()] * NUM_DIRECTIONS
    return result
def is_connect_marked (source: NavArea, target: NavArea, dir: DirectionType):
    connect_init( source )
    connect_init( target )
    return (
        target in CONNECT_LIST[source][dir.value]
        or source in CONNECT_LIST[target][OppositeDirection(dir).value]
    )
def mark_connect (source: NavArea, target: NavArea, dir: DirectionType):
    connect_init( source )
    connect_init( target )
    CONNECT_LIST[source][dir.value].add( target )
    CONNECT_LIST[target][OppositeDirection(dir).value].add( source )
def unmark_connect (source: NavArea, target: NavArea, dir: DirectionType):
    connect_init( source )
    connect_init( target )
    CONNECT_LIST[source][dir.value].discard( target )
    CONNECT_LIST[target][OppositeDirection(dir).value].discard( source )


def is_navarea_ignorable (area: NavArea, target: NavArea = None) -> bool:
    area_attr = area.attribute_flags
    return (
        not area_attr.precise
        and (
            (area_attr.crouch or area_attr.jump)
        )
    )


def is_navarea_too_high (source: Vector, target: Vector):
    return abs( target.z - source.z ) > STEP_HEIGHT


def iter_navarea_ent_encounter (area: NavArea):
    offset = Vector.from_list([ 0, 0, -HUMAN_HEIGHT_HALF ])
    for spot in area.encounter_spots.entries:
        spot: EncounterSpot = spot
        path: Ray = spot.path

        area: NavArea = spot.source.area_connection.area
        origin: Vector = path.source
        dirr: DirectionType = spot.source.direction
        yield (area, origin+offset, dirr)
        area = spot.target.area_connection.area
        origin = path.target
        dirr = spot.target.direction
        yield (area, origin+offset, dirr)


def iter_navarea_ent_connection (source: NavArea):
    """Taken from `CNavArea::DrawConnectedAreas`."""
    for connections in source.area_adjacents_per_directions:
        dir: DirectionType = connections.ks_instances_direction
        connections: list[NavConnect] = connections.entries
        for connection in connections:
            target: NavArea = connection.area
            if is_connect_marked( source, target, dir ):
                continue
            mark_connect( source, target, dir )
            f_origin: Vector = VECTOR_ZERO.copy()
            t_origin: Vector = VECTOR_ZERO.copy()
            hook_origin: Vector = VECTOR_ZERO.copy()
            size: float = 5.0
            hook_origin, _ = source.ComputePortal( target, dir )

            if dir == DirectionType.north:
                f_origin = hook_origin + Vector.from_list([ 0.0, size, 0.0 ])
                t_origin = hook_origin + Vector.from_list([ 0.0, -size, 0.0 ])
            elif dir == DirectionType.south:
                f_origin = hook_origin + Vector.from_list([ 0.0, -size, 0.0 ])
                t_origin = hook_origin + Vector.from_list([ 0.0, size, 0.0 ])
            elif dir == DirectionType.east:
                f_origin = hook_origin + Vector.from_list([ -size, 0.0, 0.0 ])
                t_origin = hook_origin + Vector.from_list([ +size, 0.0, 0.0 ])
            elif dir == DirectionType.west:
                f_origin = hook_origin + Vector.from_list([ size, 0.0, 0.0 ])
                t_origin = hook_origin + Vector.from_list([ -size, 0.0, 0.0 ])

            f_origin.z = source.GetZ( f_origin )
            t_origin.z = target.GetZ( t_origin )
            drawTo: Vector = target.GetClosestPointOnArea( t_origin )
            if is_navarea_too_high( f_origin, drawTo ):
                continue
            add_origin = Vector.from_list([ 0, 0, ENTITY_OFFSET_Z_ADD ])
            yield (target, ((f_origin + drawTo) / 2.0) + add_origin)
            yield (target, f_origin + add_origin)
            yield (target, drawTo + add_origin)


def iter_navarea_ent_inside (area: NavArea):
    ext = area.area_extent
    delta: Vector = ext.ks_instances_delta
    center: Vector = ext.ks_instances_center.copy()
    count_x = max(1, int(delta.x / AREA_INSIDE_SIZE))
    count_y = max(1, int(delta.y / AREA_INSIDE_SIZE))
    if count_x == 1 and count_y == 1:
        center.z += ENTITY_OFFSET_Z_ADD
        yield center
        return
    src = ext.lo
    target: Vector = VECTOR_ZERO.copy()
    add_x = delta.x / count_x
    add_y = delta.y / count_y
    for x in range( count_x ):
        target.update( center )
        if count_x > 1:
            target.x = src.x + add_x*(x+1)
        for y in range( count_y ):
            if count_y > 1:
                target.y = src.y + add_y*(y+1)
            target = area.get_aligned_origin( target )
            target.z += ENTITY_OFFSET_Z_ADD
            yield target


def iter_navarea_ent (areas: list[NavArea], flags: str = "c"):
    areas = list( filter((lambda x:not is_navarea_ignorable(x)), areas) )
    flags_clean = dict.fromkeys( flags.lower(), None )
    # Processing...
    for source in areas:
        for flag in flags_clean:
            if flag == "a":
                for target, origin in iter_navarea_ent_connection( source ):
                    add_node( InfoNodeEntity(source, origin, target) )
            if flag == "b":
                for target, origin, _ in iter_navarea_ent_encounter( source ):
                    add_node( InfoNodeEntity(source, origin, target) )
            if flag == "c":
                for origin in iter_navarea_ent_inside( source ):
                    add_node( InfoNodeEntity(source, origin, None) )
    # Yield the result
    for ent in sorted(
        NODE_LIST
        , key=(lambda x:
            (x.get_place()
            , [int(v) for v in x.get_id().split(";")])
        )
    ):
        if not ent.is_valid():
            raise RuntimeError( "Corrupted info_node", ent )
        yield ent


def load_navarea (path: str):
    the_nav = NavCsczFile.from_file( path )
    areas: list[NavArea] = the_nav.nav_areas.entries
    THE_NAV_AREA_GRID.load( areas )
    # Allow areas to connect to each other, etc.
    for area in areas:
        area.PostLoad()
    return (the_nav.version, areas)


def load_entities (path: str):
    the_bsp = BspFile.from_file( path )
    lump_ents: LumpContentEntities = the_bsp.lumps[BspFile.LumpType.entities.value].ks_instances_content
    return list(
        filter(
            (
                lambda x:
                not (
                    x.get("netname", "").startswith("nav2ent_")
                    and x.get("classname", "info_node")
                )
            )
            , lump_ents.blocks
        )
    )
