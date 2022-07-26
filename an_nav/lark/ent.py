import lark
from . import _MODULE_GRAMMARS



TRANSFORM_TYPE = list[dict[str,str]]


class EntTransformer (lark.Transformer):
    def string(self, s):
        (s,) = s
        return s[1:-1]
    pair = tuple
    block = dict
    start = list


_GRAMMAR, _OPTIONS = _MODULE_GRAMMARS["ent"]
_OPTIONS["transformer"] = EntTransformer()
EntLark = lark.Lark( _GRAMMAR.open(), **_OPTIONS )
"""Lark parser for `.ent` and `.bsp`'s entities lump."""


def iter_ent (o: TRANSFORM_TYPE):
    for block in o:
        yield "{\n"
        for k,v in block.items():
            yield f'"{k}" "{v}"\n'
        yield "}\n"
