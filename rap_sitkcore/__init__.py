from .read_dcm import read_dcm
from .is_dicom_xray import is_dicom_xray
from .resize import resize_and_scale_uint8
from .read_dcm_headers import read_dcm_header_pydicom
from .resize_cad4tb import resize_cad4tb
from .overlay_cad4tb import overlay_cad4tb

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

__all__ = [
    "read_dcm",
    "is_dicom_xray",
    "resize_and_scale_uint8",
    "read_dcm_header_pydicom",
    "resize_cad4tb",
    "overlay_cad4tb",
]
