import rap_sitkcore.read_dcm
from rap_sitkcore.read_dcm import _read_dcm_sitk, _read_dcm_pydicom
from rap_sitkcore._dicom_util import keyword_to_gdcm_tag
import pytest
from pathlib import Path
from .. import data_paths

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
    ],
)
def test_read_dcm1(test_file):
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


def test_read_dcm2():
    """Test with filename does not exit"""

    with pytest.raises(FileNotFoundError):
        rap_sitkcore.read_dcm(Path("ThisFileDoesNotExist.dcm"))


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
    ],
)
def test_read_dcm_pydicom(test_file, number_of_components):
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
    ],
)
def test_read_dcm_simpleitk(test_file, expected_exception, number_of_components):
    filename = data_paths[test_file]

    if expected_exception:
        with pytest.raises(RuntimeError):
            _read_dcm_sitk(Path(filename))
        return

    img = _read_dcm_sitk(Path(filename))

    assert img.GetNumberOfComponentsPerPixel() == number_of_components
