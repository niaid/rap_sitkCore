import argparse
from pathlib import Path
from typing import List, Optional, Union

import SimpleITK as sitk

from rap_sitkcore.read_dcm import read_dcm
from rap_sitkcore.resize_cad4tb import resize_cad4tb


def alpha_blend(gray_image: sitk.Image, color_image: sitk.Image, alpha: sitk.Image) -> sitk.Image:
    """
    Blend a scalar grayscale image into a vector color image, per pixel.

    :param gray_image: A scalar SimpleITK image.
    :param color_image: A vector SimpleITK image with the same size as gray_image.
    :param alpha: A SimpleITK image with pixel type sitkFloat32 and values in [0,1], the same
                    size as gray_image. 0 keeps gray_image, 1 keeps color_image.
    :return: A sitkVectorFloat32 image blending gray_image and color_image.
    """
    n = color_image.GetNumberOfComponentsPerPixel()
    # MultiplyImageFilter doesn't support vector pixels, so each channel is blended separately.
    # The (1-alpha)*gray term is the same for every channel, so it's computed once and reused.
    gray_scaled = sitk.Cast(gray_image, sitk.sitkFloat32)
    gray_scaled *= 1 - alpha

    channels = []
    for c in range(n):
        channel = sitk.VectorIndexSelectionCast(color_image, c, sitk.sitkFloat32)
        channel *= alpha
        channel += gray_scaled
        channels.append(channel)
    return sitk.Compose(channels)


def overlay_cad4tb(
    xray_image_file_path: Union[str, Path],
    cad4tb_heatmap_file_path: Union[str, Path],
    window: Optional[List[float]] = None,
) -> sitk.Image:
    """
    Overlay a CAD4TB abnormality heatmap on a chest x-ray image.

    :param xray_image_file_path: Path to the chest x-ray DICOM image file.
    :param cad4tb_heatmap_file_path: Path to the CAD4TB abnormality heatmap file (.mha).
    :param window: Optional [min, max] intensity window used to rescale the x-ray image to [0,255]
                    before overlaying, defaults to the image's own min/max.
    :return: A color (sitkVectorUInt8) SimpleITK image of the x-ray with the heatmap overlaid.
    """
    heatmap, mask = resize_cad4tb(cad4tb_heatmap_file_path, xray_image_file_path)
    image = read_dcm(Path(xray_image_file_path))

    if image.GetPixelID() != sitk.sitkUInt8:
        if window is not None:
            winmin, winmax = window
            image = sitk.Cast(sitk.IntensityWindowing(image, winmin, winmax, 0, 255), sitk.sitkUInt8)
        else:
            image = sitk.Cast(sitk.RescaleIntensity(image, 0, 255), sitk.sitkUInt8)

    heatmap[mask == 0] = 0

    color_overlay_image = sitk.ScalarToRGBColormap(heatmap, sitk.ScalarToRGBColormapImageFilter.Jet)

    # blend the heatmap in at 50% opacity, but only within the lung mask
    alpha_image = sitk.Image(mask.GetSize(), sitk.sitkFloat32) + 0.5
    alpha_image.CopyInformation(mask)
    alpha_image[mask == 0] = 0.0

    return sitk.Cast(alpha_blend(image, color_overlay_image, alpha_image), sitk.sitkVectorUInt8)


def main():
    parser = argparse.ArgumentParser(
        description="Overlay a CAD4TB abnormality heatmap on a chest x-ray image."
    )
    parser.add_argument("xray_image", help="Path to the chest x-ray DICOM image file.")
    parser.add_argument("cad4tb_heatmap", help="Path to the CAD4TB abnormality heatmap file (.mha).")
    parser.add_argument(
        "--window",
        nargs=2,
        type=float,
        metavar=("WINDOW_MIN", "WINDOW_MAX"),
        default=None,
        help="Optional intensity window min/max, defaults to the image's own min/max.",
    )
    args = parser.parse_args()

    res = overlay_cad4tb(args.xray_image, args.cad4tb_heatmap, args.window)

    xray_path = Path(args.xray_image)
    output_path = xray_path.with_name(xray_path.stem + "_overlay.png")
    sitk.WriteImage(res, output_path)


if __name__ == "__main__":
    main()
