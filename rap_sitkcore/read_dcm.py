import SimpleITK as sitk
import pydicom
from pathlib import Path
from rap_sitkcore._util import srgb2gray
from rap_sitkcore._dicom_util import (convert_float_list_to_mv_ds,
                                      convert_int_list_to_mv_ds,
                                      keyword_to_gdcm_tag)
import logging

_logger = logging.getLogger(__name__)

_keyword_to_copy = [
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "Modality",
    "PixelSpacing",
    "ImagerPixelSpacing",
    "DistanceSourceToDetector",
    "ViewPosition",
    "PatientSex",
]


def _get_string_representation(de: pydicom.dataelem.DataElement) -> str:
    """
    Get the string representation of the DICOM tag.

    Parameters:
    de (pydicom.dataelem.DataElement): The DICOM date element (a particular tag and its metadata).

    Returns:
        The string representation of the DICOM tag.
    """
    try:
        if de.value in [None, ""]:
            return ""
        elif de.VR == "DS":
            if de.VM > 1:
                return convert_float_list_to_mv_ds(de.value)
            else:
                return str(de.value)
        elif de.VR in ["US", "IS"]:

            if de.VM > 1:
                return convert_int_list_to_mv_ds(de.value)
            else:
                assert str(int(de.value)) == str(de.value), f"{de.value} != {int(de.value)}"
                return str(int(de.value))
        else:
            return str(de.value)
    except (TypeError, ValueError) as e:
        raise RuntimeError(
            f'"Error parsing data element "{de.name}" with value "{de.value}" '
            f'and value representation "{de.VR}". Error: {e}'
        )


def _read_dcm_pydicom(filename: Path, keep_all_tags: bool = False) -> sitk.Image:
    """
    Reading implementation with pydicom for DICOM
    """
    ds = pydicom.dcmread(filename)

    arr = ds.pixel_array

    if ds.PhotometricInterpretation == "MONOCHROME2":
        img = sitk.GetImageFromArray(arr, isVector=False)
    elif ds.PhotometricInterpretation == "MONOCHROME1":
        # only works with unsigned
        assert ds.PixelRepresentation == 0
        # use complement to invert the pixel intensity.
        img = sitk.GetImageFromArray(~arr, isVector=False)
    elif ds.PhotometricInterpretation in ["YBR_FULL_422", "YBR_FULL", "RGB"]:
        if ds.PhotometricInterpretation != "RGB":
            from pydicom.pixel_data_handlers.util import convert_color_space

            arr = convert_color_space(ds.pixel_array, ds.PhotometricInterpretation, "RGB")

        img = sitk.GetImageFromArray(arr, isVector=True)
    else:
        raise RuntimeError(f'Unsupported PhotometricInterpretation: "{ds.PhotometricInterpretation}"')

    # iterate through each tag in original DICOM file and copy all tags to the SimpleITK image
    if keep_all_tags:
        for de in ds:
            if de.keyword != "PixelData":
                key = f"{de.tag.group:04x}|{de.tag.elem:04x}"
                img[key] = _get_string_representation(de)
    # iterate through all tags and copy the ones specified in _keyword_to_copy
    # to the SimpleITK image
    else:
        for keyword in _keyword_to_copy:
            if keyword in ds:
                de = ds.data_element(keyword)
                key = f"{de.tag.group:04x}|{de.tag.elem:04x}"
                img[key] = _get_string_representation(de)

    return img


def _read_dcm_sitk(filename: Path, load_private_tags=False) -> sitk.Image:
    """
    Reading implementation with pydicom for DICOM
    """
    image_file_reader = sitk.ImageFileReader()
    image_file_reader.SetImageIO("GDCMImageIO")
    image_file_reader.SetFileName(str(filename))

    image_file_reader.ReadImageInformation()
    if load_private_tags:
        image_file_reader.LoadPrivateTagsOn()

    image_size = list(image_file_reader.GetSize())
    if len(image_size) == 3 and image_size[2] == 1:
        image_size[2] = 0
        image_file_reader.SetExtractSize(image_size)

    image_file_reader.GetNumberOfComponents()
    return image_file_reader.Execute()


def read_dcm(filename: Path, keep_all_tags: bool = False) -> sitk.Image:
    """
    Read an x-ray DICOM file with GDCMImageIO, reducing it to 2D from 3D as needed.
    If the file cannot be read by the GDCM library, then pydicom is tried.
    Color images are converted to grayscale.

    The pixel spacing of the output image is 1 and the direction cosine matrix is the identity.

    When keep_all_tags is False, only selected DICOM tags are present in the output image. The supported tags include:
     * "StudyInstanceUID"
     * "SeriesInstanceUID"
     * "Modality"
     * "PixelSpacing"
     * "ImagerPixelSpacing"
     * "DistanceSourceToDetector"
     * "ViewPosition"
     * "PatientSex"

    This can be overridden as needed by setting `keep_all_tags` to True. In this case,
    all tags are copied.

    :param filename: A DICOM filename
    :param keep_all_tags: If True, all DICOM tags are copied to the output image. This includes private tags. The tags
    describe the DICOM file, and image buffer transformations can be applied making the tag no longer correct.
    :returns: a 2D SimpleITK Image
    """

    if not filename.is_file():
        raise FileNotFoundError(f'The file: "{filename}" does not exist.')

    try:
        img = _read_dcm_sitk(filename, load_private_tags=keep_all_tags)
    except RuntimeError as e:
        try:
            img = _read_dcm_pydicom(filename, keep_all_tags)
        except Exception:
            # Re-raise exception from SimpleITK's GDCM reading
            raise e

    img.SetSpacing([1.0, 1.0])
    img.SetDirection([1.0, 0.0, 0.0, 1.0])

    if img.GetNumberOfComponentsPerPixel() == 1:
        out = img
    elif img.GetNumberOfComponentsPerPixel() == 3:
        out = srgb2gray(img)

        # Copy all tags
        old_keys = img.GetMetaDataKeys()

        for k in old_keys:
            out[k] = img[k]
    else:
        raise RuntimeError(f"Unsupported number of components: {img.GetNumberOfComponentsPerPixel()}")

    if not keep_all_tags:
        old_keys = set(out.GetMetaDataKeys())
        key_to_keep = {keyword_to_gdcm_tag(n) for n in _keyword_to_copy}
        for k in old_keys - key_to_keep:
            del out[k]

    return out
