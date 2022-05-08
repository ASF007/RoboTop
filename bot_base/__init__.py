import logging
from collections import namedtuple

from .cancellable_wait_for import CancellableWaitFor
from .exceptions import *
from .bot import BotBase
from .context import BotContext

__version__ = "1.4.6"


logging.getLogger(__name__).addHandler(logging.NullHandler())
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(
    major=1,
    minor=4,
    micro=6,
    releaselevel="production",
    serial=0,
)
