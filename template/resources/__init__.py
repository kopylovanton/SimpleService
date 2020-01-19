# ************* Import

from .__about__ import __version__
from .db_connection_oracle import Oracle
from .service_get import simple_app, log, ora
from .wsstats import WSStatistic
from .parmsAssertions import pAssertion
__all__ = (
    'simple_app',
    'log',
    'ora',
    'pAssertion',
    'Oracle',
    'WSStatistic',
    '__version__')
