meta:
  -author: Michael S. Booth (mike@turtlerockstudios.com), January 2003.
  -ksy-author: AnggaraNothing, July 2022.
  id: nav_cscz_file
  title: NAV
  file-extension: nav
  license: CC0-1.0
  endian: le

doc: |
  A Kaitai struct for CS 1.6/CSCZ bot AI navigation (.NAV) files.

doc-ref: |
  https://github.com/ValveSoftware/halflife/tree/master/game_shared/bot


seq:
  - id: magic_number
    type: u4
    valid: '0xFEEDFACE'
    doc: To help identify nav files.
  - id: version
    type: u4
    valid:
      expr: _ <= 5
    doc: |
      NAV version.

      Changelog:
      1 = Hiding spots as plain vector array.
      2 = Hiding spots as HidingSpot objects.
      3 = Encounter spots use HidingSpot ID's instead of storing vector again.
      4 = Includes size of source bsp file to verify nav data correlation.
      ---- Beta Release at V4 -----
      5 = Added Place info.
  - id: bsp_size
    type: u4
    if: version >= 4
    doc: |
      File size of source BSP.

      Available on version >= 4.
  - id: places
    type: place_list
    if: ks_instances_can_has_places
    doc: |
      List of places.

      Available on version >= 5.
  - id: nav_areas
    type: nav_area_list
    doc: List of navigation areas.


types:
  vector:
    -orig-id: vec3_t
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
  extent:
    -orig-id: Extent
    doc: |
      Extents of area in world coords.
      NOTE: lo.z is not necessarily the minimum Z, but corresponds to Z at point (lo.x, lo.y), etc.
    seq:
      - id: lo
        type: vector
      - id: hi
        type: vector
    instances:
      ks_instances_delta:
        value: '[hi.x - lo.x, hi.y - lo.y, hi.z - lo.z]'
        doc: hi - lo.
      ks_instances_size:
        value: 'ks_instances_delta[0] * ks_instances_delta[1]'
        doc: delta X * delta Y.
      ks_instances_center:
        value: '[(lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, (lo.z + hi.z) / 2.0]'
        doc: Centroid of area.
  ray:
    -orig-id: Ray
    seq:
      - id: source
        -orig-id: from
        type: vector
      - id: target
        -orig-id: to
        type: vector
  place_list:
    -orig-id: PlaceDirectory
    doc: |
      The 'place directory' is used to save and load places from
      nav files in a size-efficient manner that also allows for the
      order of the place ID's to change without invalidating the
      nav files.

      The place directory is stored in the nav file as a list of
      place name strings.  Each nav area then contains an index
      into that directory, or zero if no place has been assigned to
      that area.
    seq:
      - id: count
        type: u2
      - id: entries
        type: place
        repeat: expr
        repeat-expr: count
  place:
    -orig-id: Place
    doc: A place is a named group of navigation areas.
    seq:
      - id: name_length
        type: u2
        doc: Length of raw string bytes array.
      - id: name
        type: strz
        size: name_length
        encoding: ascii
        doc: Name of this place.
  nav_area_list:
    -orig-id: NavAreaList
    seq:
      - id: count
        type: u4
      - id: entries
        type: nav_area
        repeat: expr
        repeat-expr: count
  nav_area:
    -orig-id: CNavArea
    doc: |
      A CNavArea is a rectangular region defining a walkable area in the map.
    seq:
      # load ID.
      - id: id
        -orig-id: m_id
        type: u4
        doc: Unique area ID.
      # load attribute flags.
      - id: attribute_flags
        -orig-id: m_attributeFlags
        type: nav_area_attribute_flags
        size: 1
        doc: Set of attribute bit flags.
      # load extent of area.
      - id: area_extent
        -orig-id: m_extent
        type: extent
        doc: Extents of area.
      # load heights of implicit corners.
      - id: corner_northeast_z
        -orig-id: m_neZ
        type: f4
        doc: Height of the north-east corner.
      - id: corner_southwest_z
        -orig-id: m_swZ
        type: f4
        doc: Height of the south-west corner.
      # load connections (IDs) to adjacent areas
      # in the enum order NORTH, EAST, SOUTH, WEST.
      - id: area_adjacents_per_directions
        -orig-id: m_connect
        type: nav_connect_list(_index)
        repeat: expr
        repeat-expr: 4
        doc: List of adjacent areas for each direction.
      # Load hiding spots.
      - id: hiding_spots
        -orig-id: m_hidingSpotList
        type: hiding_spot_list
        doc: List of hiding spots.
      # Load number of approach areas.
      - id: approach_areas
        -orig-id: m_approach
        type: approach_info_list
        doc: List of approach areas.
      - id: encounter_spots
        -orig-id: m_spotEncounterList
        type: encounter_spot_list
        doc: List of encounter spots.
      - id: place_id
        type: u2
        if: _root.ks_instances_can_has_places
        doc: Place ID for this area.
    instances:
      ks_instances_is_undefined_place:
        value: place_id == 0
        doc: 'ie: "no place".'
      ks_instances_place:
        -orig-id: m_place
        value: _parent._parent.places.entries[place_id - 1]
        if: 'not (ks_instances_is_undefined_place)'
        doc: The Place object for this area.
      ks_instances_corner_northeast:
        value: '[area_extent.hi.x, area_extent.lo.y, corner_northeast_z]'
      ks_instances_corner_southwest:
        value: '[area_extent.lo.x, area_extent.hi.y, corner_southwest_z]'
  nav_area_attribute_flags:
    -orig-id: NavAttributeType
    meta:
      bit-endian: le
    seq:
      - id: crouch
        type: b1
        doc: Must crouch to use this node/area.
      - id: jump
        type: b1
        doc: Must jump to traverse this area.
      - id: precise
        type: b1
        doc: Do not adjust for obstacles, just move along area.
      - id: no_jump
        type: b1
        doc: Inhibit discontinuity jumping.
  nav_connect_list:
    -orig-id: NavConnectList
    params:
      - id: ks_params_index
        type: s4
    seq:
      - id: count
        type: u4
      - id: entries
        type: nav_connect
        repeat: expr
        repeat-expr: count
    instances:
      ks_instances_direction:
        value: ks_params_index
        enum: direction_type
        doc: Direction of these connections.
  nav_connect:
    -orig-id: NavConnect
    doc: The NavConnect union is used to refer to connections to areas.
    seq:
      - id: area_id
        -orig-id: id
        type: u4
        doc: NavArea ID for this connection.
  hiding_spot_list:
    -orig-id: HidingSpotList
    seq:
      - id: count
        type: u1
      - id: entries
        repeat: expr
        repeat-expr: count
        type:
          switch-on: ks_instances_is_legacy
          cases:
            true: vector
            false: hiding_spot
    instances:
      ks_instances_is_legacy:
        value: _root.version == 1
        doc: Return true if hiding spots are vectors list.
  hiding_spot:
    -orig-id: HidingSpot
    doc: |
      A HidingSpot is a good place for a bot to crouch and wait for enemies.
    seq:
      - id: id
        -orig-id: m_id
        type: u4
        doc: This spot's unique ID.
      - id: origin
        -orig-id: m_pos
        type: vector
        doc: World coordinates of the spot.
      - id: flags
        -orig-id: m_flags
        type: hiding_spot_flags
        size: 1
        doc: Bit flags.
  hiding_spot_flags:
    meta:
      bit-endian: le
    seq:
      - id: in_cover
        type: b1
        doc: In a corner with good hard cover nearby.
      - id: good_sniper_shot
        type: b1
        doc: Had at least one decent sniping corridor.
      - id: ideal_sniper_shot
        type: b1
        doc: Had see either very far, or a large area, or both.
  approach_info_list:
    seq:
      - id: count
        type: u1
      - id: entries
        type: approach_info
        repeat: expr
        repeat-expr: count
  approach_info:
    -orig-id: ApproachInfo
    seq:
      - id: here
        type: nav_connect
        doc: The approach area.
      - id: prev
        type: approach_info_connect(true)
        doc: The area just before the approach area on the path.
      - id: next
        type: approach_info_connect(false)
        doc: The area just after the approach area on the path.
  approach_info_connect:
    params:
      - id: ks_params_is_previous
        type: bool
        doc: |
          Return true if this area is prev.
          Otherwise, next area.
    seq:
      - id: area_connection
        -orig-id: area
        type: nav_connect
      - id: transverse_prev_to_here
        type: u1
        enum: transverse_type
        if: ks_params_is_previous
      - id: transverse_here_to_next
        type: u1
        enum: transverse_type
        if: not ks_params_is_previous
  encounter_spot_list:
    -orig-id: SpotEncounterList
    seq:
      - id: count
        type: u4
      - id: entries
        repeat: expr
        repeat-expr: count
        type:
          switch-on: ks_instances_is_legacy
          cases:
            true: encounter_spot_legacy
            false: encounter_spot
    instances:
      ks_instances_is_legacy:
        value: _root.version < 3
        doc: Return true if encounter spots are legacy version.
  encounter_spot_legacy:
    doc: |
      Old data, read and discard.
      No know sample files so far.
    seq:
      - id: source
        type: nav_connect
      - id: target
        type: nav_connect
      - id: path
        type: ray
      # Read list of spots along this path.
      - id: spots_count
        type: u1
      - id: spots
        type: encounter_spot_legacy_point
        repeat: expr
        repeat-expr: spots_count
  encounter_spot_legacy_point:
    seq:
      - id: unknown1
        type: vector
      - id: unknown2
        type: f4
  encounter_spot:
    -orig-id: SpotEncounter
    doc: |
      This struct stores possible path segments thru a CNavArea, and the dangerous spots
      to look at as we traverse that path segment.
    seq:
      - id: source
        -orig-id: from
        type: encounter_spot_area
      - id: target
        -orig-id: to
        type: encounter_spot_area
      # Read list of spots along this path.
      - id: spots_count
        type: u1
      - id: spots
        type: encounter_spot_order
        repeat: expr
        repeat-expr: spots_count
  encounter_spot_area:
    seq:
      - id: area_connection
        -orig-id: area
        type: nav_connect
      - id: direction
        type: u1
        enum: direction_type
  encounter_spot_order:
    -orig-id: SpotOrder
    doc: |
      Stores a pointer to an interesting "spot", and a parametric distance along a path.
    seq:
      - id: hiding_spot_id
        -orig-id: id
        type: u4
      - id: t_char
        type: u1
        doc: |
          Low-res float packed as char.
          Refer to `ks_instances_t` for float value.
    instances:
      ks_instances_t:
        -orig-id: t
        value: t_char / 255.0
        doc: |
          Parametric distance along ray where this spot first has LOS to our path.


instances:
  ks_instances_can_has_places:
    value: version >= 5
    doc: Return true if NAV file does support Place info.


enums:
  direction_type:
    # -orig-id: NavDirType
    0: north
    1: east
    2: south
    3: west
    4: num_directions
  transverse_type:
    # -orig-id: NavTraverseType
    # doc: Define possible ways to move from one area to another.
    # NOTE: First 4 directions MUST match NavDirType.
    0: go_north
    1: go_east
    2: go_south
    3: go_west
    4: go_ladder_up
    5: go_ladder_down
    6: go_jump
