meta:
  -ksy-author: AnggaraNothing, July 2022.
  -orig-id: dheader_t
  id: bsp_file
  file-extension: bsp
  license: cc0-1.0
  endian: le

doc: |
  BSP file format that's commonly used by GoldSrc engine games.

doc-ref:
  - https://github.com/valvesoftware/halflife/blob/master/utils/common/bspfile.c
  - https://github.com/valvesoftware/halflife/blob/master/utils/common/bspfile.h


seq:
  - id: version
    type: s4
    valid: 30
    doc: 'Must be 30 for a valid HL BSP file.'
  - id: lumps
    type: lump(_index)
    repeat: expr
    repeat-expr: 15
    doc: 'BSP lumps.'


types:
  lump:
    -orig-id: lump_t
    doc: |
      The BSP lump.
    params:
      - id: ks_params_index
        type: s4
    seq:
      - id: content_offset
        -orig-id: fileofs
        type: s4
        doc: 'File offset to data.'
      - id: content_size
        -orig-id: filelen
        type: s4
        doc: 'Length of data.'
    instances:
      ks_instances_type:
        value: ks_params_index
        enum: lump_type
        doc: 'Lump type.'
      ks_instances_content:
        pos: content_offset
        size: content_size
        doc: 'Lump data.'
        type:
          switch-on: ks_instances_type
          cases:
            'lump_type::entities': lump_content_entities
  lump_content_entities:
    doc: |
      Entities lump.
    seq:
      - id: blocks
        type: strz
        encoding: ascii
        size-eos: true


enums:
  lump_type:
    0: entities
    1: planes
    2: textures
    3: vertexes
    4: visibility
    5: nodes
    6: texinfo
    7: faces
    8: lighting
    9: clipnodes
    10: leafs
    11: marksurfaces
    12: edges
    13: surfedges
    14: models
