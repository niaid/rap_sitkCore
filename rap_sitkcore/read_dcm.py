import SimpleITK as sitk
import pydicom
from pathlib import Path
from rap_sitkcore._util import srgb2gray


def _read_dcm_pydicom(filename: Path) -> sitk.Image:
    """
    Reading implementation with pydicom for DICOM
    """
    ds = pydicom.dcmread(filename)
    img = sitk.GetImageFromArray(ds.pixel_array, isVector=(len(ds.pixel_array.shape) == 3))

    arr = ds.pixel_array

    if ds.PhotometricInterpretation == "MONOCHROME2":
        img = sitk.GetImageFromArray(arr, isVector=False)

    elif ds.PhotometricInterpretation == "MONOCHROME1":
        # only works with unsigned
        assert ds.PixelRepresentation == 0
        # use complement to invert the pixel intensity.
        img = sitk.GetImageFromArray(~arr, isVector=False)
    elif ds.PhotometricInterpretation in ["YBR_FULL_422", "YBR_FULL", "RGB"]:
        from pydicom.pixel_data_handlers.util import convert_color_space

        if ds.PhotometricInterpretation != "RGB":
            arr = convert_color_space(ds.pixel_array, ds.PhotometricInterpretation, "RGB")

        img = sitk.GetImageFromArray(arr, isVector=True)
    else:
        raise RuntimeError(f'Unsupported PhotometricInterpretation: "{ds.PhotometricInterpretation}"')

    if "Modality" in ds:
        de = ds.data_element("Modality")
        img.SetMetaData(f"{de.tag.group:04x}|{de.tag.elem:04x}", de.value)
    # TODO Set spacing and origin etc...

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


def read_dcm(filename: Path) -> sitk.Image:
    """
    Read an x-ray DICOM file with GDCMImageIO, reducing it to 2D from 3D as needed.
    If the file cannot be read by the GDCM library, then pydicom is tried.
    Color images are converted to grayscale.

    The pixel spacing of the output image is 1 and the direction cosine matrix is the identity.

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
        return img
    elif img.GetNumberOfComponentsPerPixel() == 3:
        return srgb2gray(img)
    raise RuntimeError(f"Unsupported number of components: {img.GetNumberOfComponentsPerPixel()}")
