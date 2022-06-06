import pytest
import requests
import time
from rap_sitkcore.read_dcm_headers import _read_dcm_header_pydicom
from .. import data_paths


@pytest.fixture(scope="module")
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


@pytest.mark.parametrize("input_file", ["1.3.6.1.4.1.25403.163683357445804.11044.20131119114627.12.dcm"])
def test_read_dcm_headers(input_file, request):
    #####################################################################
    # test with local file first
    #####################################################################
    filename = data_paths[input_file]

    local_dataset, fp_local, response_local = _read_dcm_header_pydicom(filename)

    # should be non-empty
    assert len(local_dataset.values()) != 0

    #####################################################################
    # Next test with remote file, without streaming
    #####################################################################
    presigned_url = request.getfixturevalue("remote_data_paths")[input_file]

    st = time.perf_counter()
    remote_dataset_wo_streaming, fp_wo_streaming, response_wo_streaming = _read_dcm_header_pydicom(
        presigned_url, stream=False
    )
    et = time.perf_counter()
    time_wo_streaming = et - st
    print(f"Elapsed time without streaming for {filename}:\n{time_wo_streaming} s\n")

    # DICOM filedataset should be identical - could be too stringent
    assert str(local_dataset) == str(remote_dataset_wo_streaming)

    # There should be no bytes remaining on the wire
    assert response_wo_streaming.raw.length_remaining == 0

    #####################################################################
    # Now test with remote file, with streaming
    #####################################################################
    st = time.perf_counter()
    remote_dataset_streaming, fp_streaming, response_streaming = _read_dcm_header_pydicom(presigned_url)
    et = time.perf_counter()
    time_streaming = et - st
    print(f"Elapsed time with streaming for {filename}:\n{time_streaming} s\n")

    # Dataset should be the same whether we stream or not
    assert str(remote_dataset_streaming) == str(remote_dataset_wo_streaming)

    # There should be data left on the wire here (the pixel data)
    assert response_streaming.raw.length_remaining > 0

    # This is probably a bad test - streaming should be faster than not streaming
    assert time_wo_streaming > time_streaming
