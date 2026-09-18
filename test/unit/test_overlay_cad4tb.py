import numpy as np
import pytest
import SimpleITK as sitk

from rap_sitkcore.overlay_cad4tb import overlay_cad4tb


@pytest.fixture
def cad4tb_and_xray_paths(tmp_path):
    """
    Writes a synthetic CAD4TB heatmap (background=-1, an abnormality region in [0,1])
    and a synthetic uint16 x-ray DICOM at 2x the heatmap's width/height to tmp_path.
    """
    heatmap_size = (50, 40)
    scale = 2

    heatmap_arr = np.full(heatmap_size[::-1], -1.0, dtype=np.float32)
    heatmap_arr[10:30, 10:40] = 0.75
    heatmap = sitk.GetImageFromArray(heatmap_arr)
    heatmap_path = tmp_path / "heatmap.mha"
    sitk.WriteImage(heatmap, str(heatmap_path))

    xray_size = (heatmap_size[0] * scale, heatmap_size[1] * scale)
    xray_arr = np.zeros(xray_size[::-1], dtype=np.uint16)
    # a gradient so rescale/windowing has non-trivial min/max to work with
    xray_arr[:, :] = np.linspace(100, 3000, xray_size[0], dtype=np.uint16)
    xray = sitk.GetImageFromArray(xray_arr)
    xray_path = tmp_path / "xray.dcm"
    sitk.WriteImage(xray, str(xray_path))

    return heatmap_path, xray_path, xray_size


def test_overlay_cad4tb_output_shape(cad4tb_and_xray_paths):
    heatmap_path, xray_path, xray_size = cad4tb_and_xray_paths

    result = overlay_cad4tb(xray_path, heatmap_path)

    assert result.GetSize() == xray_size
    assert result.GetNumberOfComponentsPerPixel() == 3
    assert result.GetPixelID() == sitk.sitkVectorUInt8


def test_overlay_cad4tb_outside_mask_matches_plain_xray(cad4tb_and_xray_paths):
    """Outside the lung mask, the overlay should be a pure grayscale-as-RGB rendering of the x-ray."""
    heatmap_path, xray_path, _xray_size = cad4tb_and_xray_paths

    result = overlay_cad4tb(xray_path, heatmap_path)
    result_arr = sitk.GetArrayFromImage(result)

    # (0, 0) is outside the resized abnormality region (region is roughly x in [20,80), y in [20,60))
    pixel = result_arr[0, 0]
    assert pixel[0] == pixel[1] == pixel[2]


def test_overlay_cad4tb_inside_mask_differs_from_plain_xray(cad4tb_and_xray_paths):
    """Inside the lung mask, the heatmap color should be blended in, so channels differ."""
    heatmap_path, xray_path, _xray_size = cad4tb_and_xray_paths

    result = overlay_cad4tb(xray_path, heatmap_path)
    result_arr = sitk.GetArrayFromImage(result)

    # the abnormality region (heatmap x in [10,40), y in [10,30)) is resized 2x
    # to roughly x in [20,80), y in [20,60) in the xray's coordinate space.
    pixel = result_arr[40, 50]
    assert not (pixel[0] == pixel[1] == pixel[2])


def test_overlay_cad4tb_with_explicit_window(cad4tb_and_xray_paths):
    heatmap_path, xray_path, xray_size = cad4tb_and_xray_paths

    result = overlay_cad4tb(xray_path, heatmap_path, window=[100.0, 3000.0])

    assert result.GetSize() == xray_size
    assert result.GetNumberOfComponentsPerPixel() == 3
    assert result.GetPixelID() == sitk.sitkVectorUInt8
