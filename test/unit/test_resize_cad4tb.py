import numpy as np
import pytest
import SimpleITK as sitk

from rap_sitkcore.resize_cad4tb import resize_cad4tb


def test_resize_cad4tb(tmp_path):
    # background=-1, an abnormality region in [0,1], x-ray at 2x the heatmap's width/height
    heatmap_size = (50, 40)
    scale = 2

    foreground = 0.75
    heatmap_arr = np.full(heatmap_size[::-1], -1.0, dtype=np.float32)
    heatmap_arr[10:30, 10:40] = foreground
    heatmap = sitk.GetImageFromArray(heatmap_arr)
    heatmap_path = tmp_path / "heatmap.mha"
    sitk.WriteImage(heatmap, str(heatmap_path))

    xray_size = (heatmap_size[0] * scale, heatmap_size[1] * scale)
    xray = sitk.Image(xray_size, sitk.sitkUInt16)
    xray_path = tmp_path / "xray.mha"
    sitk.WriteImage(xray, str(xray_path))

    abnormality_map, lung_mask = resize_cad4tb(heatmap_path, xray_path)

    assert abnormality_map.GetSize() == xray_size
    assert lung_mask.GetSize() == xray_size
    assert abnormality_map.GetSpacing() == lung_mask.GetSpacing()
    assert abnormality_map.GetOrigin() == lung_mask.GetOrigin()

    # Check that min and max of abnormality mask are as expected
    stats = sitk.StatisticsImageFilter()
    stats.Execute(abnormality_map)
    assert stats.GetMinimum() == pytest.approx(0.0, abs=1e-5)
    assert stats.GetMaximum() == pytest.approx(foreground, abs=1e-2)

    # mask values are 0 or 1
    assert set(sitk.GetArrayViewFromImage(lung_mask).flatten()) == {0, 1}

    # the abnormality region is 20 rows x 30 cols scaled up 2x in both dimensions
    expected_count = 20 * 30 * 4
    assert sitk.GetArrayViewFromImage(lung_mask).sum() == pytest.approx(expected_count, rel=0.05)
