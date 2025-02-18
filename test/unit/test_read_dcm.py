import rap_sitkcore.read_dcm
from rap_sitkcore.read_dcm import _read_dcm_sitk, _read_dcm_pydicom
from rap_sitkcore._dicom_util import keyword_to_gdcm_tag
import pytest
from pathlib import Path
import SimpleITK as sitk

_white_listed_dicom_tags = [
    "0020|000d",
    "0020|000e",
    "0008|0060",
    "0028|0030",
    "0018|1164",
    "0018|1110",
    "0018|5101",
    "0010|0040",
]


@pytest.mark.parametrize(
    "test_file",
    [
        "1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm",
        "1.3.6.1.4.1.25403.158515237678667.5060.20130807021253.18.dcm",
        "1.2.840.114062.2.192.168.196.13.2015.11.4.13.11.45.13871156.dcm",
        "2.25.288816364564751018524666516362407260298.dcm",
        "2.25.240995260530147929836761273823046959883.dcm",
        "2.25.226263219114459199164755074787420926696.dcm",
        "2.25.40537326380965754670062689705190363681.dcm",
        "2.25.326714092011492114153708980185182745084.dcm",
        "2.25.5871713374023139953558641168991505875.dcm",
        "n10.dcm",
        "n11.dcm",
        "n12.dcm",
        "1.2.392.200036.9116.2.5.1.37.2429823676.1495586039.603772.DCM",
        "2.25.298570032897489859462791131067889681111.dcm",
        "non_square_color.dcm",
        "non_square_uint16.dcm",
        "square_uint8.dcm",
    ],
)
def test_read_dcm1(test_file, data_paths):
    """ """

    filename = data_paths[test_file]

    img = rap_sitkcore.read_dcm(Path(filename))

    assert img.GetNumberOfPixels() > 0
    assert img.GetNumberOfComponentsPerPixel() == 1
    assert img.GetDimension() == 2
    assert img.GetSpacing() == (1.0, 1.0)
    assert img.GetDirection() == (1.0, 0.0, 0.0, 1.0)

    required_tags = [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "Modality",
    ]

    for tag in required_tags:
        key = keyword_to_gdcm_tag(tag)
        assert key in img

    for k in img.GetMetaDataKeys():
        assert k in _white_listed_dicom_tags


@pytest.mark.parametrize(
    "test_file",
    [
        "1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm",
        "1.3.6.1.4.1.25403.158515237678667.5060.20130807021253.18.dcm",
        "1.2.840.114062.2.192.168.196.13.2015.11.4.13.11.45.13871156.dcm",
        "2.25.288816364564751018524666516362407260298.dcm",
        "2.25.240995260530147929836761273823046959883.dcm",
        "2.25.226263219114459199164755074787420926696.dcm",
        "2.25.40537326380965754670062689705190363681.dcm",
        "2.25.326714092011492114153708980185182745084.dcm",
        "2.25.5871713374023139953558641168991505875.dcm",
        "n10.dcm",
        "n11.dcm",
        "n12.dcm",
        "1.2.392.200036.9116.2.5.1.37.2429823676.1495586039.603772.DCM",
        "2.25.298570032897489859462791131067889681111.dcm",
        "non_square_color.dcm",
        # "non_square_uint16.dcm",
        # "square_uint8.dcm" The 0018|1164 float tags don't match
    ],
)
def test_read_dcm_pydicom_tags(test_file, data_paths):
    """
    Tests for correct reading of tags from DICOM files between the pydicom and SimpleITK implementations.
    """
    filename = Path(data_paths[test_file])

    required_tags = [
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "Modality",
    ]

    pydicom_img = _read_dcm_pydicom(Path(filename))
    for tag in required_tags:
        key = keyword_to_gdcm_tag(tag)
        assert key in pydicom_img

    for k in pydicom_img.GetMetaDataKeys():
        assert k in _white_listed_dicom_tags

    img_keys = set(pydicom_img.GetMetaDataKeys())

    for tag in required_tags:
        key = keyword_to_gdcm_tag(tag)
        assert key in pydicom_img

    std_img = rap_sitkcore.read_dcm(filename)

    assert len(img_keys) == len(
        std_img.GetMetaDataKeys()
    ), f"Number of keys don't match. SymDifference: {img_keys ^ set(std_img.GetMetaDataKeys())}"

    for k in img_keys:
        assert k in std_img.GetMetaDataKeys()
        assert pydicom_img[k].rstrip(" ") == std_img[k].rstrip(
            " "
        ), f"Values don't match for key: {k} pydicom: '{pydicom_img[k]}' std_img: '{std_img[k]}'"

    pydicom_img = _read_dcm_pydicom(Path(filename), keep_all_tags=True)

    if "6000|3000" in pydicom_img.GetMetaDataKeys():
        del pydicom_img["6000|3000"]

    img_keys = set(pydicom_img.GetMetaDataKeys())

    std_img = rap_sitkcore.read_dcm(filename, keep_all_tags=True)

    for tag in ("ITK_original_direction", "ITK_original_spacing"):
        if tag in std_img.GetMetaDataKeys():
            del std_img[tag]

    assert len(img_keys) == len(std_img.GetMetaDataKeys()), (
        f"Number of keys don't match.  pydicom Difference: "
        f"{set(pydicom_img.GetMetaDataKeys()) - set(std_img.GetMetaDataKeys())} "
        f"std_img Difference: {set(std_img.GetMetaDataKeys()) - set(pydicom_img.GetMetaDataKeys())}"
    )

    for k in img_keys:
        assert k in std_img.GetMetaDataKeys()
        # if k is a private tag where the first group number is odd don't compare
        if int(k.split("|")[0], 16) % 2:
            continue
        assert pydicom_img[k].rstrip(" ") == std_img[k].rstrip(
            " "
        ), f"With Keep all, values don't match for key: {k} pydicom: '{pydicom_img[k]}' std_img: '{std_img[k]}'"


def test_read_dcm2():
    """Test with filename does not exit"""

    with pytest.raises(FileNotFoundError):
        rap_sitkcore.read_dcm(Path("ThisFileDoesNotExist.dcm"))


@pytest.mark.parametrize(
    "file_name,image_size,image_md5,modality",
    [
        ("non_square_color.dcm", (3555, 2894), "7c865539fa50739991d11ab39970fd66", "XC"),
        ("non_square_uint16.dcm", (2828, 2320), "78d3b4d4aeb6debaec3b5905272df572", "CR"),
        ("square_uint8.dcm", (2630, 2529), "f5dec5a1ae076040e7e2d365666d26cb", "CR"),
        ("2.25.298570032897489859462791131067889681111.dcm", (4000, 3000), "9eae70e3f4601c19e88feb63d31fd92e", "CR"),
    ],
)
def test_read_dcm3(file_name, image_size, image_md5, modality, data_paths):
    """Test migrated from tbp_image_refresh_thumbnail"""
    dicom_tag_modality = "0008|0060"

    filename = data_paths[file_name]
    img = rap_sitkcore.read_dcm(Path(filename))

    assert img.GetSize() == image_size
    assert sitk.Hash(img, function=sitk.HashImageFilter.MD5) == image_md5
    assert img.GetMetaData(dicom_tag_modality) == modality


@pytest.mark.parametrize(
    ("test_file", "number_of_components"),
    [
        ("1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm", 1),
        ("1.3.6.1.4.1.25403.158515237678667.5060.20130807021253.18.dcm", 1),
        ("1.2.840.114062.2.192.168.196.13.2015.11.4.13.11.45.13871156.dcm", 1),
        ("2.25.288816364564751018524666516362407260298.dcm", 3),
        ("2.25.240995260530147929836761273823046959883.dcm", 1),
        ("2.25.226263219114459199164755074787420926696.dcm", 1),
        ("2.25.40537326380965754670062689705190363681.dcm", 3),
        ("2.25.326714092011492114153708980185182745084.dcm", 3),
        ("2.25.5871713374023139953558641168991505875.dcm", 1),
        ("n10.dcm", 1),
        ("n11.dcm", 1),
        ("n12.dcm", 1),
        ("1.2.392.200036.9116.2.5.1.37.2429823676.1495586039.603772.DCM", 1),
        ("2.25.298570032897489859462791131067889681111.dcm", 1),
        ("non_square_color.dcm", 3),
        ("non_square_uint16.dcm", 1),
        ("square_uint8.dcm", 1),
    ],
)
def test_read_dcm_pydicom(test_file, number_of_components, data_paths):
    filename = data_paths[test_file]

    img = _read_dcm_pydicom(Path(filename))

    assert img.GetNumberOfComponentsPerPixel() == number_of_components


@pytest.mark.parametrize(
    ("test_file", "expected_exception", "number_of_components"),
    [
        ("1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm", False, 1),
        ("1.3.6.1.4.1.25403.158515237678667.5060.20130807021253.18.dcm", False, 1),
        ("1.2.840.114062.2.192.168.196.13.2015.11.4.13.11.45.13871156.dcm", False, 1),
        ("2.25.288816364564751018524666516362407260298.dcm", False, 3),
        ("2.25.240995260530147929836761273823046959883.dcm", True, 1),
        ("2.25.226263219114459199164755074787420926696.dcm", True, 1),
        ("2.25.40537326380965754670062689705190363681.dcm", False, 3),
        ("2.25.326714092011492114153708980185182745084.dcm", False, 3),
        ("2.25.5871713374023139953558641168991505875.dcm", True, 1),
        ("n10.dcm", False, 1),
        ("n11.dcm", False, 1),
        ("n12.dcm", False, 1),
        ("1.2.392.200036.9116.2.5.1.37.2429823676.1495586039.603772.DCM", True, 1),
        ("1.2.840.113704.9.1000.16.2.201903221237504530000100020001.I10", True, 1),
        ("2.25.298570032897489859462791131067889681111.dcm", True, 1),
        ("non_square_color.dcm", False, 3),
        ("non_square_uint16.dcm", False, 1),
        ("square_uint8.dcm", False, 1),
    ],
)
def test_read_dcm_simpleitk(test_file, expected_exception, number_of_components, data_paths):
    filename = data_paths[test_file]

    if expected_exception:
        with pytest.raises(RuntimeError):
            _read_dcm_sitk(Path(filename))
        return

    img = _read_dcm_sitk(Path(filename))

    assert img.GetNumberOfComponentsPerPixel() == number_of_components
