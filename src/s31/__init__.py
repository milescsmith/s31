from importlib.metadata import PackageNotFoundError, version
from loguru import logger

# logger.disable("s31")

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"