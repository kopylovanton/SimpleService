# ************* Import

from .__about__ import __version__
from .db_connection_oracle import Oracle
from .service_get import app, log, ora, parms
from .wsstats import WSStatistic
from .parmsAssertions import pAssertion
__all__ = (
    'app',
    'log',
    'ora',
    'pAssertion',
    'Oracle',
    'WSStatistic',
    'parms',
    '__version__')
