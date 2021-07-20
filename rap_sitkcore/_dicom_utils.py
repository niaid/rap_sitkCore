from typing import List

# Value Multiplicity delimiter
_vm_delimiter = "\\"


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
    Convert a iterable of float to the DICOM mutli-value representation for decimal string (DS).

    This method is intended to convert the pydicom MV DS data elements to the representation that GDCM produced for
    SimpleITK.

    :param value: an iterable or list like object of convertable to float values.
    :returns: The value encode in for DICOM representation.
    """

    rep = _vm_delimiter.join([str(float(f)) for f in value])

    # DICOM spec
    if len(rep) % 2:
        rep += " "

    return rep
