# ************* Import
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from .__about__ import __version__
from .service_handler import ApiHandler

__all__ = (
    'ApiHandler',
    '__version__')
