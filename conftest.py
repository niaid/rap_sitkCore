import pytest
import requests


@pytest.fixture(scope="module")
def data_paths():
    """
    A dictionary of test data file names to full paths.
    """
    from pathlib import Path

    path_dic = {}
    for p in (Path(__file__).parent / "test" / "data").glob("*"):
        if p.is_file():
            path_dic[p.name] = str(p.absolute())
    return path_dic


@pytest.fixture(scope="session")
def remote_data_paths():
    # Get s3 URL to DICOM files in TBPORTALS
    # TODO: try to work around doing this, some of the tests will break if DEPOT updates their DICOMS.
    # I couldn't find an easy way to set up a local server to test our data_paths that could implement streaming.
    # This could probably be implemented by modifying the python http.server BaseHTTPRequestHandler, but ideally
    # there is an easier way than that.
    payloads = [
        {
            "directory": (
                "00069df2-2406-43b6-8c58-5f5e164c7e35/"
                "1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.10/"
                "1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.11"
            ),
            "objectKey": "1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm",
        }
    ]
    presigned_urls = requests.post(
        "https://depotapi.tbportals.niaid.nih.gov/api/Amazon/GetBulkPresignedUrls", json=payloads
    ).json()
    yield {payload["objectKey"]: presigned_urls[i] for i, payload in enumerate(payloads)}
