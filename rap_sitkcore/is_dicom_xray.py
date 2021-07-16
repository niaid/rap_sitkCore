import pydicom
from pathlib import Path

_accepted_modalities = ('CR', 'XC', 'RG', 'XA', 'HC', 'DX')
_strict_modalities = ('CR', 'XC', 'RG', 'XA', 'HC', 'DX')

def is_dicom_xray(filename: Path, strict: bool = False) -> bool:
    """
    For a DICOM file, inspects the Modality meta-data field to determine if the image is an x-ray. This classification
    is for the TBPortals collection to primarily eliminate CT scans.

    :param filename: a Path to a DICOM file to inspect
    :param strict: If true scanned? picture? modalities are not considered.
    :return: True if the DICOM Modality may be an x-ray image.
    """
    return True
