""" Functions related to retrieving the dicom headers from a file """

import pydicom
import requests
from pathlib import Path
from io import SEEK_SET, SEEK_END
from typing import Any, Union


class _ResponseStream(object):
    """
    This is a file-like wrapper around a requests content iterator.  It is modified
    very slightly from this gist:

    https://gist.github.com/obskyr/b9d4b4223e7eaf4eedcd9defabb34f13

    Python's requests package provides a file-like response attribute 'response.raw', but it
    is not seekable, which pydicom uses in dcmread.  This interface provides a seekable file-like
    wrapper around a requests content iterator.

    See also:
    https://2.python-requests.org/en/master/user/quickstart/#raw-response-content
    """

    def __init__(self, request_iterator, bytes_io_implementation=pydicom.filebase.DicomBytesIO):
        """
        :param self:
        :param request_iterator: a requests content iterator
        :param bytes_io_implementation: BytesIO implementation
        """
        self._bytes = bytes_io_implementation()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

            self._bytes.seek(left_off_at)
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)


"""
TODO: The choice of default download chunk size is arbitrary here and needs some testing to determine an ideal value,
if there is one.

If we set it too high, we might overshoot the start of the pixel data section and unnecessarily download pixel data.
If we set it too low, we might suffer from accumulated overhead as we iterate through small chunks.

Some quick tests on one image (only the chunk_size parameter is varied):

    In [93]: times = {}
    ...: def time_calls():
    ...:     for n in [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]:
    ...:         st = time.perf_counter()
    ...:         dcm, fp, response = do_the_call(new_url, True, True, n)  # This is the actual call
    ...:         et = time.perf_counter()
    ...:         times[n] = {'elapsed-time': et - st, 'length_remaining': response.raw.length_remaining}

    In [94]: time_calls()

    In [96]: times
    Out[96]:
    {1: {'elapsed-time': 0.29127729699757765, 'length_remaining': 12247104},
    10: {'elapsed-time': 0.18592952999824774, 'length_remaining': 12247104},
    100: {'elapsed-time': 0.14632360899850028, 'length_remaining': 12247104},
    1000: {'elapsed-time': 0.17851408800197532, 'length_remaining': 12247104},
    10000: {'elapsed-time': 0.1341154009969614, 'length_remaining': 12238104},
    100000: {'elapsed-time': 0.18739204599842196, 'length_remaining': 12148104},
    1000000: {'elapsed-time': 0.2897699749992171, 'length_remaining': 11248104},
    10000000: {'elapsed-time': 1.1952385980002873, 'length_remaining': 2248104}}
"""


def _read_dcm_header_pydicom(
    filepath_or_url: Union[str, Path], download_chunk_size_bytes: int = 10240, stream: bool = True, **kwargs: Any
) -> tuple:
    """
    Get the DICOM headers from either a local file (by file path) or a remote file (by URL).

    :param filepath_or_url: A string containing either a path or a URL.  The URL must be prefixed by either
                    'http://' or 'https://'. Or a filepath as a pathlib Path object.
    :param download_chunk_size_bytes: An integer controlling the download chunk size if the file is remote,
                    defaults to 1024 bytes.
    :param stream: A boolean indicating whether the HTTP request (if filepath_or_url points to a remote file)
                    should be streamed.

                    If filepath_or_url points to a local file, this parameter is ignored.
                    -------
                    For this to work, the server must support the chunked transfer-encoding.  If it doesn't, requests
                    *should* treat this as a normal request and download the entire request contents before passing to
                    pydicom dcmread.
                    --------
    :param kwargs: keywords are forwarded to pydicom.dcmread
    :returns: tuple of the following format:
                   (
                       pydicom.dataset.FileDataset: the pydicom file dataset object,
                       'fp': the object that pydicom reads from - a ResponseStream for remote files or a path for
                             local ones,
                       'response': the raw requests response
                   )
    """
    response = None
    if isinstance(filepath_or_url, Path):
        fp = filepath_or_url
    else:
        # Try to see if filepath_or_url is a valid url
        try:
            # Make request; could/should make this a session for repeated requests.
            response = requests.get(filepath_or_url, stream=stream)
        except requests.exceptions.MissingSchema:
            # There wasn't an http or https, so treat this as a local file
            fp = Path(filepath_or_url)
        else:
            # create a seekable interface into requests content iterator
            fp = _ResponseStream(response.iter_content(download_chunk_size_bytes))
    # Return the object that pydicom reads from and the raw requests response (for testing purposes).
    return (pydicom.dcmread(fp=fp, stop_before_pixels=True, **kwargs), fp, response)


def read_dcm_header_pydicom(
    filepath_or_url: Union[str, Path], download_chunk_size_bytes: int = 10240, stream: bool = True, **kwargs: Any
) -> pydicom.dataset.FileDataset:
    """
    Get the DICOM headers from either a local file (by file path) or a remote file (by URL).

    :param filepath_or_url: A string containing either a path or a URL.  The URL must be prefixed by either
                    'http://' or 'https://'. Or a filepath as a pathlib Path object.
    :param download_chunk_size_bytes: An integer controlling the download chunk size if the file is remote,
                    defaults to 1024 bytes.
    :param stream: A boolean indicating whether the HTTP request (if filepath_or_url points to a remote file)
                    should be streamed.

                    If filepath_or_url points to a local file, this parameter is ignored.

                    For this to work, the server must support the chunked transfer-encoding.  If it doesn't, requests
                    *should* treat this as a normal request and download the entire request contents before passing to
                    pydicom dcmread.

    :param kwargs: keywords are forwarded to pydicom.dcmread
    :returns: a pydicom.dataset.FileDataset representing the DICOM indicated by filepath_or_url
    """
    return _read_dcm_header_pydicom(
        filepath_or_url=filepath_or_url, download_chunk_size_bytes=download_chunk_size_bytes, stream=stream, **kwargs
    )[0]
