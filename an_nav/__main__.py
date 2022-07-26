import argparse
import pathlib
from .lark.ent import iter_ent
from .utils import (
    load_navarea
    , load_entities
    , iter_navarea_ent
)



parser = argparse.ArgumentParser(
    prog='nav2ent.py'
    , description=(
        'Convert `.NAV` into `info_node` entities.\n' \
        'Different build flag order might be resulting different output.'
    )
)
parser.add_argument(
    'bsp_file'
    , type=pathlib.Path
    , help='BSP file path. The NAV file must be located at same directory.'
)
parser.add_argument(
    '--build-flag', '-f'
    , type=str
    , dest="order"
    , default='c'
    , help=str((
        'a = Build info_node from connections.'
        , 'b = Build info_node from encounter data.'
        , 'c = Build info_node inside of nav area (min. 1 entity created).'
        , 'Default "c"'
    ))
)
args = parser.parse_args()


bsp_file = args.bsp_file
nav_version, nav_areas = load_navarea( str(bsp_file.with_suffix(".nav")) )
print(
    f"NAV Version: {nav_version}"
    , f"NAV Area Count: {len(nav_areas)}"
    , sep="\n"
)


infonode_total = 0
with bsp_file.with_suffix(".ent").open( "w", encoding='ascii' ) as fp:
    fp.writelines( iter_ent(load_entities(str(bsp_file))) )
    print( "BSP Entities:", fp.tell(), "byte(s)" )

    flags_clean = dict.fromkeys( args.order.lower(), None )
    print( "info_node Build Order:" )
    for flag in flags_clean:
        txt = None
        if flag == "a":
            txt = 'Connections per area'
        elif flag == "b":
            txt = 'Encounter spots per area'
        elif flag == "c":
            txt = 'Inside of area, if area too small, 1 at the center'
        else:
            raise argparse.ArgumentError( "order", f"Unknown flag {flag}" )
        print( '-', txt )
    print()

    for ent in iter_navarea_ent( nav_areas, flags=args.order ):
        print([
            ent.get_id()
            , ent.get_place()
        ])
        fp.write( str(ent) )
        infonode_total += 1

    print(
        f"info_node Total: {infonode_total}"
        , sep="\n"
    )
