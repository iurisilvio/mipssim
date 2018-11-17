import os
import sys

_path = os.path.dirname(__file__)
os.chdir(_path)
sys.path.insert(0, _path)

import bottle
import server

application = bottle.default_app()
