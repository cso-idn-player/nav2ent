from pathlib import Path as _Path



_MODULE_DIR = _Path( __file__ ).parent
_MODULE_GRAMMARS = dict[str, tuple[_Path, dict]]()


# Store all .lark file paths.
for subpath in _MODULE_DIR.iterdir():
    if not subpath.is_file():
        continue

    if subpath.suffix.lower() != ".lark":
        continue

    options = {}
    suffixes = subpath.suffixes[:-1]
    if len(suffixes) >= 2:
        options["lexer"] = suffixes[-2].lower().lstrip(".")
    if len(suffixes) >= 1:
        options["parser"] = suffixes[-1].lower().lstrip(".")

    _MODULE_GRAMMARS[subpath.name.split(".")[0].lower()] = ( (subpath, options,) )
