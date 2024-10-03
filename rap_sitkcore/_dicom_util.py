from typing import List
import pydicom

# Value Multiplicity delimiter
_vm_delimiter = "\\"


def _pad_to_even_length(rep: str) -> str:
    """
    Pad the given string to an even length by adding a space at the end.

    :param rep: the string to pad
    :returns: the padded string
    """

    if len(rep) % 2:
        return rep + " "
    return rep


def convert_mv_ds_to_float_list(rep: str, vm: int = 0) -> List[float]:
    """
    Converts the file representation, into data for a multi-value Decimal String (DS).

    :param rep: the representation of attribute occurring in the file
    :param vm: the expected Value Multiplicity of rep, if 0 then any number of multivalues is accepted
    :returns: a list of float converted from rep
    """

    ds_list = rep.split(_vm_delimiter)

    if vm != 0 and len(ds_list) != vm:
        raise ValueError(f'"{rep}" has {len(ds_list)} values, but expected {vm}.')

    return [float(ds) for ds in ds_list]


def convert_float_list_to_mv_ds(value: List[float]) -> str:
    """
    Convert a iterable of float to the DICOM multi-value representation for decimal string (DS).

    This method is intended to convert the pydicom MV DS data elements to the representation that GDCM produced for
    SimpleITK.

    :param value: an iterable or list like object of convertable to float values.
    :returns: The value encode in for DICOM representation.
    """

    # convert to string with 6 decimal places, but maximum 2 trailing zeros
    rep = _vm_delimiter.join([f"{f:.6f}" for f in value])

    return _pad_to_even_length(rep)


def convert_int_list_to_mv_ds(value: List[float]) -> str:
    """
    Convert a iterable of int to the DICOM multi-value representation for (unsigned) integer (US/IS).

    This method is intended to convert the pydicom MV DS data elements to the representation that GDCM produced for
    SimpleITK.

    :param value: an iterable or list like object of convertable to float values.
    :returns: The value encode in for DICOM representation.
    """

    rep = _vm_delimiter.join([str(int(f)) for f in value])

    return _pad_to_even_length(rep)


def keyword_to_gdcm_tag(keyword: str) -> str:
    """Converts a DICOM keyword to a DICOM tag formatted as a string to match GDCM representation.

    Example: "SeriesDescription"-> "0008|103e"

    :param keyword: a string representation of a DICOM metadata keyword, following the defined camel case convention
    :returns: a string representation of the keyword as a metadata tag, consisting of the group in hex, a '|'
     deliminator and the element in hex.

    """
    tag = pydicom.tag.Tag(keyword)
    return f"{tag.group:04x}|{tag.elem:04x}"
