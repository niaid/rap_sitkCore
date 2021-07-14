import rap_sitkcore.read_dcm
import pytest
from pathlib import Path
from .. import data_paths


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
def test_expected_results(test_file):
    """ """

    filename = data_paths[test_file]

    img = rap_sitkcore.read_dcm(Path(filename))

    assert img.GetNumberOfPixels() > 0
