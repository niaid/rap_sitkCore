import SimpleITK as sitk
from pathlib import Path
from typing import Tuple, Union


def resize_cad4tb(
    cad4tb_file_path: Union[str, Path], image_file_path: Union[str, Path]
) -> Tuple[sitk.Image, sitk.Image]:
    """
    Resample a CAD4TB abnormality map and its lung mask to match the geometry
    of the original x-ray image.

    The CAD4TB image combines both the abnormality score, values in [0,1], and a
    mask structure, background denoted by -1. The width of the CAD4TB image is
    scaled to the original image width and that scale factor is also applied
    to the height (the CAD4TB image was rescaled from the original to a specific
    width and the height is set so that the original aspect ratio is retained).

    The abnormality map and mask are separated before rescaling so that resampling
    does not introduce values in (-1,0) that did not exist in the original CAD4TB
    image.

    :param cad4tb_file_path: Path to the CAD4TB abnormality map file.
    :param image_file_path: Path to the original x-ray image file whose geometry is
                    used as the resampling reference.
    :return: A tuple of (abnormality_map, lung_mask), both resampled to the geometry of the original x-ray
                    image. abnormality_map values are in [0,1] and lung_mask is a binary mask.
    """
    file_reader = sitk.ImageFileReader()
    file_reader.SetFileName(cad4tb_file_path)
    cad4tb_abnormality_map = file_reader.Execute()

    # Get the image information without reading the pixel data.
    file_reader.SetFileName(image_file_path)
    file_reader.ReadImageInformation()
    image_size = file_reader.GetSize()[0:2]
    image_spacing = file_reader.GetSpacing()[0:2]
    image_origin = file_reader.GetOrigin()[0:2]

    lung_mask = cad4tb_abnormality_map > -1
    abnormality_map = cad4tb_abnormality_map
    abnormality_map[abnormality_map < 0] = 0

    tx = sitk.Similarity2DTransform()
    tx.SetScale(cad4tb_abnormality_map.GetWidth() / image_size[0])

    abnormality_map.SetSpacing(image_spacing)
    abnormality_map = sitk.Resample(
        abnormality_map,
        image_size,
        tx,
        sitk.sitkLinear,
        image_origin,
        image_spacing,
        [1, 0, 0, 1],
        0,
        cad4tb_abnormality_map.GetPixelID(),
    )

    lung_mask.SetSpacing(image_spacing)
    lung_mask = sitk.Resample(
        lung_mask,
        image_size,
        tx,
        sitk.sitkNearestNeighbor,
        image_origin,
        image_spacing,
        [1, 0, 0, 1],
        0,
        lung_mask.GetPixelID(),
    )

    return abnormality_map, lung_mask
