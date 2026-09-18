import argparse
from pathlib import Path
from typing import List, Optional, Union

import SimpleITK as sitk

from rap_sitkcore.read_dcm import read_dcm
from rap_sitkcore.resize_cad4tb import resize_cad4tb


def mask_image_multiply(mask: sitk.Image, image: sitk.Image) -> sitk.Image:
    """
    Multiply a scalar mask with a scalar or vector image, channel by channel.

    :param mask: A scalar SimpleITK image.
    :param image: A scalar or vector SimpleITK image with the same size as mask.
    :return: The pixel-wise product of mask and image.
    """
    components_per_pixel = image.GetNumberOfComponentsPerPixel()
    if components_per_pixel == 1:
        return mask * image
    else:
        return sitk.Compose(
            [
                mask * sitk.VectorIndexSelectionCast(image, channel)
                for channel in range(components_per_pixel)
            ]
        )


def alpha_blend(
    image1: sitk.Image,
    image2: sitk.Image,
    alpha: Union[float, sitk.Image] = 0.5,
    mask1: Optional[sitk.Image] = None,
    mask2: Optional[sitk.Image] = None,
) -> sitk.Image:
    """
    Alpha blend two images, pixels can be scalars or vectors.

    The alpha blending factor can be either a scalar or an image whose pixel type is sitkFloat32 and
    values are in [0,1]. The region that is alpha blended is controlled by the given masks.

    :param image1: A scalar or vector SimpleITK image.
    :param image2: A scalar or vector SimpleITK image, with the same size as image1.
    :param alpha: A scalar or a SimpleITK image with pixel type sitkFloat32 and values in [0,1].
    :param mask1: Region of image1 to blend, defaults to the entire image.
    :param mask2: Region of image2 to blend, defaults to the entire image.
    :return: The alpha blended image.
    """

    if not mask1:
        mask1 = sitk.Image(image1.GetSize(), sitk.sitkFloat32) + 1.0
        mask1.CopyInformation(image1)
    else:
        mask1 = sitk.Cast(mask1, sitk.sitkFloat32)
    if not mask2:
        mask2 = sitk.Image(image2.GetSize(), sitk.sitkFloat32) + 1
        mask2.CopyInformation(image2)
    else:
        mask2 = sitk.Cast(mask2, sitk.sitkFloat32)
    # if we received a scalar, convert it to an image
    if not isinstance(alpha, sitk.Image):
        alpha = sitk.Image(image1.GetSize(), sitk.sitkFloat32) + alpha
        alpha.CopyInformation(image1)
    components_per_pixel = image1.GetNumberOfComponentsPerPixel()
    if components_per_pixel > 1:
        img1 = sitk.Cast(image1, sitk.sitkVectorFloat32)
        img2 = sitk.Cast(image2, sitk.sitkVectorFloat32)
    else:
        img1 = sitk.Cast(image1, sitk.sitkFloat32)
        img2 = sitk.Cast(image2, sitk.sitkFloat32)

    intersection_mask = mask1 * mask2

    intersection_image = mask_image_multiply(
        alpha * intersection_mask, img1
    ) + mask_image_multiply((1 - alpha) * intersection_mask, img2)
    return (
        intersection_image
        + mask_image_multiply(mask2 - intersection_mask, img2)
        + mask_image_multiply(mask1 - intersection_mask, img1)
    )


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

    float_mask = sitk.Cast(mask, sitk.sitkFloat32)
    heatmap *= float_mask

    color_overlay_image = sitk.ScalarToRGBColormap(heatmap, sitk.ScalarToRGBColormapImageFilter.Jet)
    return sitk.Cast(
        alpha_blend(sitk.Compose([image] * 3), color_overlay_image, alpha=0.5, mask2=mask),
        sitk.sitkVectorUInt8,
    )


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
