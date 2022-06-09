from pydicom.errors import InvalidDicomError
from pathlib import Path
from rap_sitkcore.read_dcm_headers import read_dcm_header_pydicom
from typing import Union


import logging

_logger = logging.getLogger(__name__)

_strict_modalities = ("CR", "RG", "XA", "DX")
_acceptable_modalities = _strict_modalities + (
    "HC",
    "XC",
)


def is_dicom_xray(filepath_or_url: Union[str, Path], strict: bool = False) -> bool:
    """
    For a DICOM file, inspects the Modality meta-data field to determine if the image is an x-ray. This classification
    is for the TBPortals collection to primarily x-ray from CT scans.

    If the filename is not in DICOM format, then false is returned.
    If the filename does not refer to a file, then the "FileNotFound" exception will be thrown.

    :param filepath_or_url: A string containing either a path or a URL.  The URL must be prefixed by either
                    'http://' or 'https://'. Or a filepath as a pathlib Path object.
    :param strict: If true scanned? picture? modalities are not considered.
    :return: True if the DICOM Modality may be an x-ray image.
    """

    try:
        with read_dcm_header_pydicom(filepath_or_url, specific_tags=["Modality"]) as ds:
            _logger.debug(f'"{str(filepath_or_url)}" has "{ds.Modality}" modality.')
            if strict:
                return ds.Modality in _strict_modalities
            return ds.Modality in _acceptable_modalities

    except InvalidDicomError:
        return False
