try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version(__name__)
except ImportError:
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        __version__ = get_distribution(__name__).version
    except DistributionNotFound:
        # package is not installed
        pass
except PackageNotFoundError:
    # package is not installed
    pass

__author__ = ["Bradley Lowekamp"]

__all__ = []
