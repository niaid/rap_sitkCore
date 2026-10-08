import numpy as np
import SimpleITK as sitk

from rap_sitkcore.overlay_cad4tb import overlay_cad4tb


def test_overlay_cad4tb(tmp_path):
    # Background=-1, an abnormality region in [0,1], x-ray at 2x the heatmap dimensions.
    heatmap_size = (50, 40)
    scale = 2
    foreground = 0.75

    heatmap_arr = np.full(heatmap_size[::-1], -1.0, dtype=np.float32)
    heatmap_arr[10:30, 10:40] = foreground
    heatmap = sitk.GetImageFromArray(heatmap_arr)
    heatmap_path = tmp_path / "heatmap.mha"
    sitk.WriteImage(heatmap, str(heatmap_path))

    xray_size = (heatmap_size[0] * scale, heatmap_size[1] * scale)
    xray_arr = np.zeros(xray_size[::-1], dtype=np.uint16)
    xray_arr[:, :] = np.linspace(100, 3000, xray_size[0], dtype=np.uint16)
    xray = sitk.GetImageFromArray(xray_arr)
    xray.SetSpacing((0.160145, 0.160114))
    xray_path = tmp_path / "xray.dcm"
    sitk.WriteImage(xray, str(xray_path))

    result = overlay_cad4tb(xray_path, heatmap_path)

    assert result.GetSize() == xray_size
    assert result.GetNumberOfComponentsPerPixel() == 3
    assert result.GetPixelID() == sitk.sitkVectorUInt8

    result_arr = sitk.GetArrayViewFromImage(result)
    # The abnormality spans x=[20,80), y=[20,60) after resizing.
    # Values outside abnormality are grayscale, inside have color.
    outside_pixel = result_arr[0, 0]
    assert outside_pixel[0] == outside_pixel[1] == outside_pixel[2]
    inside_pixel = result_arr[40, 50]
    assert not (inside_pixel[0] == inside_pixel[1] == inside_pixel[2])

    windowed_result = overlay_cad4tb(xray_path, heatmap_path, window=[100.0, 3000.0])
    assert windowed_result.GetSize() == xray_size
    assert windowed_result.GetNumberOfComponentsPerPixel() == 3
    assert windowed_result.GetPixelID() == sitk.sitkVectorUInt8
