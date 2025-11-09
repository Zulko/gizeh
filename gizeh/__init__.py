""" gizeh/__init__.py """

# __all__ = []

from .gizeh import *
from .geometry import *

try:
    from importlib.metadata import version
    __version__ = version("gizeh")
except ImportError:
    # For Python < 3.8
    from importlib_metadata import version
    __version__ = version("gizeh")
