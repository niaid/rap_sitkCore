import SimpleITK as sitk


def srgb2gray(img: sitk.Image) -> sitk.Image:
    """
    Convert an sRGB [0, 255] image to gray scale and rescale results to [0,255].

    :param img: SimpleITK Image with 3 components, any dimension.
    :returns: scalar SimpleITK Image of UInt8
    """
    num_channels = img.GetNumberOfComponentsPerPixel()
    assert num_channels == 3
    channels = [
        sitk.VectorIndexSelectionCast(img, i, sitk.sitkFloat32) for i in range(img.GetNumberOfComponentsPerPixel())
    ]
    # linear mapping
    img_builder = 1 / 255.0 * (0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2])
    # nonlinear gamma correction
    img_builder = (
        img_builder * sitk.Cast(img_builder <= 0.0031308, sitk.sitkFloat32) * 12.92
        + img_builder ** (1 / 2.4) * sitk.Cast(img_builder > 0.0031308, sitk.sitkFloat32) * 1.055
        - 0.55
    )
    # TODO use shift scale which include a output pixel type option ( requires SimpleITK 2.1 )
    return sitk.Cast(sitk.RescaleIntensity(img_builder), sitk.sitkUInt8)
