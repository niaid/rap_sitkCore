import rap_sitkcore.is_dicom_xray
import pytest
from pathlib import Path
import os
import tempfile


@pytest.mark.parametrize(
    ("test_file", "is_xray"),
    [
        ("1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm", True),
        ("1.3.6.1.4.1.25403.158515237678667.5060.20130807021253.18.dcm", True),
        ("1.2.840.114062.2.192.168.196.13.2015.11.4.13.11.45.13871156.dcm", True),
        ("2.25.288816364564751018524666516362407260298.dcm", True),
        ("2.25.240995260530147929836761273823046959883.dcm", True),
        ("2.25.226263219114459199164755074787420926696.dcm", True),
        ("2.25.40537326380965754670062689705190363681.dcm", True),
        ("2.25.326714092011492114153708980185182745084.dcm", True),
        ("2.25.5871713374023139953558641168991505875.dcm", True),
        ("n10.dcm", False),  # "OT" modality
        ("n11.dcm", False),  # "OT" modality
        ("n12.dcm", False),  # "OT" modality
    ],
)
def test_is_dicom_xray1(test_file, is_xray, data_paths):
    """ """

    filename = data_paths[test_file]

    assert rap_sitkcore.is_dicom_xray(Path(filename)) == is_xray
    assert rap_sitkcore.is_dicom_xray(str(filename)) == is_xray


def test_is_dicom_xray2():
    """Test with filename does not exit"""

    with pytest.raises(FileNotFoundError):
        rap_sitkcore.is_dicom_xray(Path("ThisFileDoesNotExist.dcm"))


def test_is_dicom_xray3():
    extensions = [
        ".jpg",
        ".JPG",
        ".jpeg",
        ".JPEG",
        ".dcm",
        ".DCM",
        ".dicom",
        ".png",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        for ext in extensions:
            fpath = Path(tmp_dir) / f"image{ext}"

            with open(fpath, "wb") as fout:
                fout.write(os.urandom(1024 * 10))

            assert not rap_sitkcore.is_dicom_xray(fpath)


@pytest.mark.parametrize(
    ("test_file", "is_xray"),
    [
        ("1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm", True),
        ("1.3.6.1.4.1.25403.158515237678667.5060.20130807021253.18.dcm", True),
        ("1.2.840.114062.2.192.168.196.13.2015.11.4.13.11.45.13871156.dcm", True),
        ("2.25.288816364564751018524666516362407260298.dcm", False),  # "XC" modality
        ("2.25.240995260530147929836761273823046959883.dcm", True),
        ("2.25.226263219114459199164755074787420926696.dcm", True),
        ("2.25.40537326380965754670062689705190363681.dcm", False),  # "XC" modality
        ("2.25.326714092011492114153708980185182745084.dcm", False),  # "XC" modality
        ("2.25.5871713374023139953558641168991505875.dcm", True),
        ("n10.dcm", False),  # "OT" modality
        ("n11.dcm", False),  # "OT" modality
        ("n12.dcm", False),  # "OT" modality
        ("1.2.392.200036.9116.2.5.1.37.2429823676.1495586039.603772.DCM", False),
        ("1.2.840.113704.9.1000.16.2.201903221237504530000100020001.I10", False),  # "SR" modality
        ("2.25.298570032897489859462791131067889681111.dcm", True),
        ("non_square_color.dcm", False),
        ("non_square_uint16.dcm", True),
        ("square_uint8.dcm", True),
    ],
)
def test_is_dicom_xray4(test_file, is_xray, data_paths):
    """Testing with strict option"""

    filename = data_paths[test_file]

    assert rap_sitkcore.is_dicom_xray(Path(filename), strict=True) == is_xray


@pytest.mark.parametrize(
    ("test_file", "is_xray"), [("1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm", True)]
)
def test_is_dicom_xray5(test_file, is_xray, remote_data_paths):
    url = remote_data_paths[test_file]
    assert rap_sitkcore.is_dicom_xray(url, strict=True) == is_xray
