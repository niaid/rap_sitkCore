import SimpleITK as sitk
import pydicom
from pathlib import Path
from rap_sitkcore._util import srgb2gray
from rap_sitkcore._dicom_util import convert_float_list_to_mv_ds, keyword_to_gdcm_tag
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

    if keep_all_tags:
    # if keep all tags is true, we copy all tags from the pydicom dataset to the SimpleITK image.
        try:
            ds = pydicom.dcmread(filename, stop_before_pixels=True)

            for data_element in ds:
                key_sitk = f"({data_element.tag.group:04x}|{data_element.tag.elem:04x})"
                name = data_element.name
                value = data_element.value
                VR = data_element.VR
                VM = data_element.VM

                if value in [None, ""]:
                    img[key_sitk] = ""
                elif VR == "DS":
                    if VM > 1:
                        img[key_sitk] = convert_float_list_to_mv_ds(value)
                    else:
                        img[key_sitk] = str(float(value))
                elif VR == "US":
                    img[key_sitk] = str(int(value))
                else:
                    img[key_sitk] = value
        except TypeError as te:
            print(f'"{filename}" had an error parsing at "{name}" with value "{value}" and value representation "{VR}". Error: {te}')
        except ValueError as ve:
            print(f'"{filename}" had an error parsing at "{name}" with value "{value}" and value representation "{VR}". Error: {ve}')
            

    else: 
        for tag in _keyword_to_copy:
            if tag in ds:
                de = ds.data_element(tag)
                key = f"{de.tag.group:04x}|{de.tag.elem:04x}"
                if de.value is None:
                    img[key] = ""
                elif de.VR == "DS":
                    if de.VM > 1:
                        img[key] = convert_float_list_to_mv_ds(de.value)
                    else:
                        img[key] = str(float(de.value))
                elif de.VR in ["CS", "UI"]:
                    img[key] = de.value
                else:
                    raise ValueError(
                        f'"{filename}" has data element "{de.name}" non-conforming value representation "{de.VR}".'
                    )

    return img


def _read_dcm_sitk(filename: Path) -> sitk.Image:
    """
    Reading implementation with pydicom for DICOM
    """
    image_file_reader = sitk.ImageFileReader()
    image_file_reader.SetImageIO("GDCMImageIO")
    image_file_reader.SetFileName(str(filename))

    image_file_reader.ReadImageInformation()

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

    Only selected DICOM tags are present in the output image. The supported tags include:
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
    :returns: a 2D SimpleITK Image
    """

    if not filename.is_file():
        raise FileNotFoundError(f'The file: "{filename}" does not exist.')

    try:
        img = _read_dcm_sitk(filename)
    except RuntimeError as e:
        try:
            img = _read_dcm_pydicom(filename)
        except Exception:
            # Re-raise exception from SimpleITK's GDCM reading
            raise e

    img.SetSpacing([1.0, 1.0])
    img.SetDirection([1.0, 0.0, 0.0, 1.0])

    if img.GetNumberOfComponentsPerPixel() == 1:
        if not keep_all_tags:
            old_keys = img.GetMetaDataKeys()
            key_to_keep = [keyword_to_gdcm_tag(n) for n in _keyword_to_copy]
            for k in old_keys:
                if k not in key_to_keep:
                    del img[k]
                    
        return img
    elif img.GetNumberOfComponentsPerPixel() == 3:
        out = srgb2gray(img)
        # copy tags
        if not keep_all_tags:
            for tag_name in _keyword_to_copy:
                key = keyword_to_gdcm_tag(tag_name)
                if key in img:
                    out[key] = img[key]

        return out
    raise RuntimeError(f"Unsupported number of components: {img.GetNumberOfComponentsPerPixel()}")
