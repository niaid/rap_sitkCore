from rap_sitkcore import read_dcm, resize_and_scale_uint8
import pytest
from pathlib import Path
from .. import data_paths
import SimpleITK as sitk


@pytest.mark.parametrize(
    "file_name,thumbnail_size,md5_hash",
    [
        ("non_square_color.dcm", (256, 256), "7fb3fa09f1e5ac1c7376334ebc6f07c2"),
        ("non_square_uint16.dcm", (256, 256), "3f9ef4f27775ecab75586a319ae4bfe5"),
        ("square_uint8.dcm", (256, 256), "e8358046f74f0977f2e55df97bab0318"),
    ],
)
def test_dcm_thumbnail(file_name, thumbnail_size, md5_hash):

    filename = data_paths[file_name]
    img = read_dcm(Path(filename))

    thumbnail_img = resize_and_scale_uint8(img, thumbnail_size)

    assert thumbnail_img.GetSize() == thumbnail_size
    assert sitk.Hash(thumbnail_img, function=sitk.HashImageFilter.MD5) == md5_hash
    assert thumbnail_img.GetNumberOfComponentsPerPixel() == 1
    assert thumbnail_img.GetPixelID() == sitk.sitkUInt8
