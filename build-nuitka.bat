poetry install
poetry run python -m nuitka nuitka-nav2ent.py --standalone --mingw64 --output-dir=./dist --include-package=an_nav --include-package-data=lark --include-data-files=an_nav/lark/*.lark=an_nav/lark/ --include-data-files=an_nav/kaitai/*.ksy=an_nav/kaitai/
