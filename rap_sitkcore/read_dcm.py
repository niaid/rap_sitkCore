import SimpleITK as sitk
import pydicom
from pathlib import Path


def _read_dcm_pydicom(filename: Path) -> sitk.Image:
    """
    Reading implementation with pydicom for DICOM
    """
    ds = pydicom.dcmread(filename)
    img = sitk.GetImageFromArray(ds.pixel_array, isVector=(len(ds.pixel_array.shape) == 3))
    if img.GetNumberOfComponentsPerPixel() != 1:
        img = sitk.VectorMagnitude(img)
    if "Modality" in ds:
        de = ds.data_element("Modality")
        img.SetMetaData(f"{de.tag.group:04x}|{de.tag.elem:04x}", de.value)
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

    return image_file_reader.Execute()


def read_dcm(filename: Path) -> sitk.Image:
    """
    Read an x-ray DICOM file with GDCMImageIO, reducing it to 2D from 3D as needed.
    If the file cannot be read by the GDCM library, then pydicom is tried.
    :param filename: A DICOM filename
    :return: a 2D SimpleITK Image
    """

    if not filename.is_file():
        raise IOError(f'The file: "{filename}" does not exist.')

    try:
        return _read_dcm_sitk(filename)
    except RuntimeError as e:
        try:
            return _read_dcm_pydicom(filename)
        except Exception:
            # Reraise exception from SimpleITK's GDCM reading
            raise e
