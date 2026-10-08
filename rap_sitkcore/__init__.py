from .read_dcm import read_dcm
from .is_dicom_xray import is_dicom_xray
from .resize import resize_and_scale_uint8
from .read_dcm_headers import read_dcm_header_pydicom
from .resize_cad4tb import resize_cad4tb

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    pass

__author__ = ["Bradley Lowekamp"]


def __getattr__(name):
    if name == "overlay_cad4tb":
        from .overlay_cad4tb import overlay_cad4tb

        return overlay_cad4tb
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "read_dcm",
    "is_dicom_xray",
    "resize_and_scale_uint8",
    "read_dcm_header_pydicom",
    "resize_cad4tb",
    "overlay_cad4tb",
]
