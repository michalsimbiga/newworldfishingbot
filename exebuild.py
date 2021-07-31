from distutils.core import setup
import py2exe

setup(console=[{"script": "new_world_main.py"}],
      options={"py2exe": {"verbose": 4}}, )
