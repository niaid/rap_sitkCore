import numpy as np
import pytest
import SimpleITK as sitk

from rap_sitkcore.resize_cad4tb import resize_cad4tb


@pytest.fixture
def cad4tb_and_xray_paths(tmp_path):
    """
    Writes a synthetic CAD4TB heatmap (background=-1, an abnormality region in [0,1])
    and a synthetic x-ray image at 2x the heatmap's width/height to tmp_path.
    """
    heatmap_size = (50, 40)
    scale = 2

    heatmap_arr = np.full(heatmap_size[::-1], -1.0, dtype=np.float32)
    heatmap_arr[10:30, 10:40] = 0.75
    heatmap = sitk.GetImageFromArray(heatmap_arr)
    heatmap_path = tmp_path / "heatmap.mha"
    sitk.WriteImage(heatmap, str(heatmap_path))

    xray_size = (heatmap_size[0] * scale, heatmap_size[1] * scale)
    xray = sitk.Image(xray_size, sitk.sitkUInt16)
    xray_path = tmp_path / "xray.mha"
    sitk.WriteImage(xray, str(xray_path))

    return heatmap_path, xray_path, xray_size, scale


def test_resize_cad4tb_sizes_and_geometry(cad4tb_and_xray_paths):
    heatmap_path, xray_path, xray_size, _scale = cad4tb_and_xray_paths

    abnormality_map, lung_mask = resize_cad4tb(heatmap_path, xray_path)

    assert abnormality_map.GetSize() == xray_size
    assert lung_mask.GetSize() == xray_size
    assert abnormality_map.GetSpacing() == lung_mask.GetSpacing()
    assert abnormality_map.GetOrigin() == lung_mask.GetOrigin()


def test_resize_cad4tb_abnormality_map_values(cad4tb_and_xray_paths):
    heatmap_path, xray_path, _xray_size, _scale = cad4tb_and_xray_paths

    abnormality_map, _lung_mask = resize_cad4tb(heatmap_path, xray_path)

    stats = sitk.StatisticsImageFilter()
    stats.Execute(abnormality_map)

    # background (-1) is clipped to 0, in-range values are unchanged by resampling scale
    assert stats.GetMinimum() == pytest.approx(0.0, abs=1e-5)
    assert stats.GetMaximum() == pytest.approx(0.75, abs=1e-2)


def test_resize_cad4tb_lung_mask_is_binary(cad4tb_and_xray_paths):
    heatmap_path, xray_path, _xray_size, _scale = cad4tb_and_xray_paths

    _abnormality_map, lung_mask = resize_cad4tb(heatmap_path, xray_path)

    stats = sitk.StatisticsImageFilter()
    stats.Execute(sitk.Cast(lung_mask, sitk.sitkFloat32))

    assert stats.GetMinimum() == 0.0
    assert stats.GetMaximum() == 1.0

    # the abnormality region is 20 rows x 30 cols out of the 40x50 heatmap,
    # scaled up 2x in both dimensions
    label_stats = sitk.LabelStatisticsImageFilter()
    label_stats.Execute(lung_mask, lung_mask)
    foreground_count = label_stats.GetCount(1)
    expected_count = 20 * 30 * (2**2)
    assert foreground_count == pytest.approx(expected_count, rel=0.05)
