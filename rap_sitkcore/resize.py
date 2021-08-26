import SimpleITK as sitk
from typing import List


def resize_and_scale_uint8(image: sitk.Image, new_size: List[int]) -> sitk.Image:
    """
    Resize the given image to the given size, with isotropic pixel spacing
    and scale the intensities to [0,255].

    Resizing retains the original aspect ratio, with the original image centered
    in the new image. Zero padding is added outside the original image extent.

    :param image: A SimpleITK image.
    :param new_size: List of ints specifying the new image size.
    :return: a 2D SimpleITK image with desired size and a pixel type of sitkUInt8
    """

    new_spacing = [
        ((osz - 1) * ospc) / (nsz - 1) for ospc, osz, nsz in zip(image.GetSpacing(), image.GetSize(), new_size)
    ]
    new_spacing = [max(new_spacing)] * image.GetDimension()
    center = image.TransformContinuousIndexToPhysicalPoint([sz / 2.0 for sz in image.GetSize()])
    new_origin = [c - c_index * nspc for c, c_index, nspc in zip(center, [sz / 2.0 for sz in new_size], new_spacing)]
    final_image = sitk.Resample(image, size=new_size, outputOrigin=new_origin, outputSpacing=new_spacing)

    # Rescale intensities if scalar image with pixel type that isn't sitkUInt8.
    if final_image.GetPixelID() == sitk.sitkUInt8:
        pass
    elif final_image.GetNumberOfComponentsPerPixel() == 1:
        final_image = sitk.Cast(sitk.RescaleIntensity(final_image), sitk.sitkUInt8)
    else:
        raise ValueError(
            "Intensity scaling is not supported for image with "
            f"{final_image.GetNumberOfComponentsPerPixel()} components and "
            f'pixel type of "{image.GetPixelIDTypeAsString()}"'
        )
    return final_image
